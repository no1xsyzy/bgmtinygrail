import math
from datetime import datetime, timedelta

import click
from termcolor import colored

from ._base import TG_PLAYER
from ._helpers import parse_target
from ..tinygrail import (
    TICO,
    TTemple,
    ServerSentError,
    ico_minimal_investment_for_level,
    ico_now_level_by_investment,
    ico_now_level_by_investors,
    ico_minimal_investors_for_level,
    ico_offerings_for_level,
    get_my_ico,
    batch_character_info,
    get_full_holding_2,
)


def level_colors(level):
    if level == 0:
        return colored(f"{level:^5}", 'grey', 'on_white', ['reverse', 'bold'])
    elif level == 1:
        return colored(f"{level:^5}", 'white', 'on_green')
    elif level == 2:
        return colored(f"{level:^5}", 'white', 'on_cyan')
    elif level == 3:
        return colored(f"{level:^5}", 'yellow', 'on_white', ['reverse', 'bold'])
    elif level == 4:
        return colored(f"{level:^5}", 'white', 'on_yellow')
    elif level == 5:
        return colored(f"{level:^5}", 'white', 'on_magenta')
    elif level == 6:
        return colored(f"{level:^5}", 'red', 'on_white', ['reverse', 'bold'])
    else:
        return colored(f"{level:^5}", 'black', 'on_white')


def time_color(end_date):
    edge1 = timedelta(hours=1)
    edge2 = timedelta(days=1)
    edge3 = timedelta(days=7)

    def dark_red(s):
        return colored(s, 'red', attrs=['dark'])

    def normal_red(s):
        return colored(s, 'red')

    def bright_red(s):
        return colored(s, 'red', attrs=['bold'])

    str_end_date = str(end_date).strip()
    now = datetime.now().replace(microsecond=0)
    rest = end_date - now
    if rest < edge1:
        prefix_len = int(len(str_end_date) * (1 - rest / edge1))
        return dark_red(str_end_date[:prefix_len]) + normal_red(str_end_date[prefix_len:])
    elif rest < edge2:
        prefix_len = int(len(str_end_date) * (1 - (rest - edge1) / (edge2 - edge1)))
        return normal_red(str_end_date[:prefix_len]) + bright_red(str_end_date[prefix_len:])
    elif rest < edge3:
        prefix_len = int(len(str_end_date) * (1 - (rest - edge2) / (edge3 - edge2)))
        return bright_red(str_end_date[:prefix_len]) + str_end_date[prefix_len:]
    return str_end_date


def fall_to_met(value):
    return f"{value}" if value > 0 else colored("(met)", 'grey', attrs=['bold'])


def colored_comparison(actual, target):
    if actual < target:
        return colored(str(actual), 'red')
    elif actual > target:
        return colored(str(actual), 'cyan')
    else:
        return f"{actual}"


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('targets', type=str, nargs=-1)
@click.option('-f', '--from-file', type=click.File('r', encoding='utf-8'), multiple=True, default=[])
@click.option('-o', '--output-format', default='simple')
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, targets, from_file, show_exceeds, output_format):
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
                initialized[cid] = [f"#{cid}", character.name, f"{th}/{tt}",
                                    colored(f"{ch}/{ct}", 'green') if ch + ct >= th + tt and ct < tt else
                                    f"{colored_comparison(ch, th)}/{colored_comparison(ct, tt)}"]
        else:
            if (th, tt) != (0, 0):
                checks.append(cid)

    if checks:
        for c in batch_character_info(player, checks):
            cid = c.character_id
            th, tt = parsed_targets[cid]
            if isinstance(c, TICO):
                try:
                    my_initial = get_my_ico(player, c.id)
                    my_investment = my_initial.amount
                except ServerSentError as e:
                    if e.message != '尚未参加ICO。':
                        raise
                    my_investment = 0
                total_investment = c.total
                total_investors = c.users
                end_date = c.end.replace(tzinfo=None)
                colored_end_date = time_color(end_date)
                lo_lv, up_lv = sorted((ico_now_level_by_investment(total_investment),
                                       ico_now_level_by_investors(total_investors)))
                if lo_lv < 1:
                    lo_lv = 1
                for level in range(lo_lv, up_lv + 2):
                    min_investment = ico_minimal_investment_for_level(level)
                    min_investors = ico_minimal_investors_for_level(level)
                    offerings = ico_offerings_for_level(level)
                    more_investment = max(0, min_investment - total_investment)
                    more_investors = max(0, min_investors - total_investors)
                    stocks_for_me = th + tt
                    stocks_for_others = offerings - stocks_for_me
                    investment_others_part = total_investment - my_investment + more_investors * 5000
                    investment_my_part = max(
                        math.ceil(investment_others_part / stocks_for_others * stocks_for_me),
                        ico_minimal_investment_for_level(level) / ico_offerings_for_level(level) * stocks_for_me)
                    more_investment_my_part = investment_my_part - my_investment
                    in_initial.append([(end_date, level), [
                        f"#{cid}", c.name, colored_end_date, f"{th}/{tt}({th + tt})",
                        level_colors(level), f"{offerings}",
                        f"{my_investment}", f"{total_investment}", f"{total_investors}",
                        fall_to_met(more_investment), fall_to_met(more_investors),
                        f"{investment_my_part}", fall_to_met(more_investment_my_part),
                    ]])
                in_initial.append([(end_date, 100), []])
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
                            ('CID', '名字', '结束时间', '目标',
                             'Lv', '总发行',
                             colored('自投入₵', 'yellow'), colored('总投入₵', 'yellow'), colored('人数', 'yellow'),
                             '还需₵', '还需人数',
                             '目标投入₵', '还需投入₵'),
                            output_format, disable_numparse=True
                            ))

    if not in_initial and not initialized:
        click.echo("Nothing to show")
