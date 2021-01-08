import math
from typing import List

import click
from click.utils import LazyFile

from ._base import TG_PLAYER
from ._helpers import parse_target
from ..tinygrail import ServerSentError, ico_minimal_investment_for_level, ico_now_level_by_investment, \
    ico_now_level_by_investors, ico_minimal_investors_for_level, ico_offerings_for_level
from ..tinygrail.api import batch_character_info, get_full_holding_2, my_initial_for_character
from ..tinygrail.model import TICO, TTemple


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('targets', type=str, nargs=-1)
@click.option('-f', '--from-file', type=click.File('r', encoding='utf-8'), multiple=True, default=[])
@click.option('-o', '--output-format', default='simple')
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, targets: List[str], from_file: List[LazyFile], show_exceeds, output_format):
    def iterates():
        for file in from_file:
            for line in file:
                line = line.rstrip()
                if line and not line.startswith("--"):
                    yield line
        for target in targets:
            for t in target.split(","):
                yield t

    parsed_targets = parse_target(iterates())
    if not any(i != (0, 0) for i in parsed_targets.items()):
        print("no target specified at all")
        raise click.exceptions.Exit(11)
    characters = get_full_holding_2(player)

    initialized = {}
    in_initial = []

    checks = []
    for cid, (th, tt) in parsed_targets.items():
        if character := characters.get(cid):
            if isinstance(character, TTemple):
                ch = 0
                ct = character.sacrifices
            else:
                ch, ct = character.state, character.sacrifices
            if (not (ch >= th and ct >= tt)) or (show_exceeds and not (ch == th and ct == tt)):
                def colored(actual, target):
                    if actual < target:
                        return f"\033[31m{actual}\033[0m"
                    elif actual > target:
                        return f"\033[36m{actual}\033[0m"
                    else:
                        return f"{actual}"

                initialized[cid] = [f"#{cid}", character.name, f"{th}/{tt}",
                                    f"\033[32m{ch}/{ct}\033[0m" if ch + ct >= th + tt and ct < tt else
                                    f"{colored(ch, th)}/{colored(ct, tt)}"]
        else:
            if (th, tt) != (0, 0):
                checks.append(cid)

    if checks:
        for c in batch_character_info(player, checks):
            cid = c.character_id
            th, tt = parsed_targets[cid]
            if isinstance(c, TICO):
                try:
                    my_initial = my_initial_for_character(player, c.id)
                    my_investment = my_initial.amount
                except ServerSentError as e:
                    if e.message != '尚未参加ICO。':
                        raise
                    my_investment = 0
                total_investment = c.total
                total_investors = c.users
                end_date = c.end.replace(tzinfo=None)
                lo_lv, up_lv = sorted((ico_now_level_by_investment(total_investment),
                                       ico_now_level_by_investors(total_investors)))
                if lo_lv < 1:
                    lo_lv = 1
                for level in range(lo_lv, up_lv + 2):
                    min_investment = ico_minimal_investment_for_level(level)
                    min_investors = ico_minimal_investors_for_level(level)
                    offerings = ico_offerings_for_level(level)
                    more_investment = min_investment - total_investment
                    more_investors = min_investors - total_investors
                    stocks_for_me = th + tt
                    stocks_for_others = offerings - stocks_for_me
                    investment_others_part = total_investment - my_investment + more_investors * 5000
                    investment_my_part = max(
                        math.ceil(investment_others_part / stocks_for_others * stocks_for_me),
                        ico_minimal_investment_for_level(level) / ico_offerings_for_level(level) * stocks_for_me)
                    more_investment_my_part = investment_my_part - my_investment
                    in_initial.append([
                        (end_date, 1),
                        [f"#{cid}", c.name, f"{end_date}", f"{th}/{tt}({th + tt})",
                         f"{level}", f"{offerings}", f"{my_investment}", f"{total_investment}", f"{total_investors}",
                         (f"{more_investment}" if more_investment > 0 else "(met)"),
                         (f"{more_investors}" if more_investors > 0 else "(met)"),
                         f"{investment_my_part}",
                         (f"{more_investment_my_part}" if more_investment_my_part > 0 else "(met)"),
                         ]])
            else:
                initialized[cid] = [f"#{cid}", c.name, f"{th}/{tt}", "-"]
            checks.remove(cid)

    from tabulate import tabulate
    if initialized:
        click.echo("In market:")
        click.echo(tabulate([initialized[key] for key in sorted(initialized.keys())],
                            ('CID', 'Name', 'Target', 'Actual'),
                            output_format))

    if in_initial and initialized:
        click.echo()

    if in_initial:
        click.echo("ICOs:")
        click.echo(tabulate([x[1] for x in sorted(in_initial, key=lambda x: x[0])],
                            ('CID', 'Name', 'End Date', 'Target',
                             'Lv', '总发行', '自投入₵', '总投入₵', '人数',
                             '还需₵', '还需人数', '目标投入₵', '还需投入₵'),
                            output_format))

    if not in_initial and not initialized:
        click.echo("Nothing to show")
