import io
import math
import pydoc
from datetime import datetime, timedelta

import click
from tabulate import tabulate
from termcolor import colored

from ._base import TG_PLAYER
from ._helpers import Targets
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


def _check_current(parsed_targets, player, show_exceeds, show_on_market):
    initialized = {}
    checks = []
    characters = get_full_holding_2(player)
    for cid, parsed_target in parsed_targets.items():
        if character := characters.get(cid):
            if isinstance(character, TTemple):
                ch = 0
                ct = character.sacrifices
            else:
                ch, ct = character.state, character.sacrifices
            if show_on_market:
                check = parsed_target.check(ch, ct)
                if check == 'sacrifice' or check[0] == 'low' or check[1] == 'low' or (
                        show_exceeds and check != ('match', 'match')):
                    initialized[cid] = [f"#{cid}", character.name, str(parsed_target),
                                        parsed_target.colored_comparison(ch, ct)]
        else:
            if parsed_target:
                checks.append(cid)
    return checks, initialized


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('targets', type=str, nargs=-1)
@click.option('-f', '--from-file', type=click.File('r', encoding='utf-8'), multiple=True, default=[])
@click.option('-o', '--output-format', default='simple')
@click.option('--show-exceeds/--hide-exceeds')
@click.option('--show-initials/--hide-initials', default=True)
@click.option('--show-on-market/--hide-on-market', default=True)
@click.option('--show-targets/--hide-targets')
def check_targets(player, targets, from_file, output_format, show_exceeds, show_initials, show_on_market, show_targets):
    if not show_initials and not show_on_market and not show_targets:
        click.echo("Not showing anything", err=True)
        raise click.exceptions.Exit(99)

    parsed_targets = Targets()
    parsed_targets.init_macros()

    for file in from_file:
        with file:
            for line in file:
                line = line.rstrip()
                try:
                    parsed_targets.load_line(line)
                except:
                    click.echo(f"error when parsing line `{line}'", err=True)
                    raise
    for target in targets:
        for t in target.split(","):
            parsed_targets.load_line(t)

    parsed_targets.cleanup_macros()

    if show_targets:
        for key in sorted(parsed_targets.keys()):
            parsed_target = parsed_targets[key]
            click.echo(f"{key} = {parsed_target}")

    if not any(parsed_targets.values()):
        print("no target specified at all")
        raise click.exceptions.Exit(11)

    in_initial = []
    checks, initialized = _check_current(parsed_targets, player, show_exceeds, show_on_market)

    if checks:
        for c in batch_character_info(player, checks):
            cid = c.character_id
            parsed_target = parsed_targets[cid]
            stocks_for_me = parsed_target.holding_min + parsed_target.tower_min
            if isinstance(c, TICO):
                if show_initials:
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
                        stocks_for_others = offerings - stocks_for_me
                        investment_others_part = total_investment - my_investment + more_investors * 5000
                        investment_my_part = max(
                            math.ceil(investment_others_part / stocks_for_others * stocks_for_me),
                            ico_minimal_investment_for_level(level) / ico_offerings_for_level(level) * stocks_for_me)
                        more_investment_my_part = investment_my_part - my_investment
                        in_initial.append([(end_date, level), [
                            f"#{cid}", c.name, colored_end_date, f"{parsed_target}({stocks_for_me})",
                            level_colors(level), f"{offerings}",
                            f"{my_investment}", f"{total_investment}", f"{total_investors}",
                            fall_to_met(more_investment), fall_to_met(more_investors),
                            f"{investment_my_part}", fall_to_met(more_investment_my_part),
                        ]])
                    in_initial.append([(end_date, 100), []])
            else:
                if show_on_market:
                    initialized[cid] = [f"#{cid}", c.name, str(parsed_target),
                                        parsed_target.colored_comparison(0, 0)]
            checks.remove(cid)

    if not initialized and not in_initial:
        click.echo("Nothing to show", err=True)
        raise click.exceptions.Exit(99)

    with io.StringIO() as output:
        if initialized:
            print("In market:", file=output)
            print(tabulate([initialized[key] for key in sorted(initialized.keys())],
                           ('CID', 'Name', 'Target', 'Actual'),
                           output_format), file=output)

        if in_initial and initialized:
            print(file=output)

        if in_initial:
            print("ICOs:", file=output)
            sorted_in_initial = [x[1] for x in sorted(in_initial, key=lambda x: x[0])]
            while not sorted_in_initial[-1]:
                del sorted_in_initial[-1]
            print(tabulate(sorted_in_initial,
                           ('CID', '名字', '结束时间', '目标',
                            'Lv', '总发行',
                            colored('自投入₵', 'yellow'), colored('总投入₵', 'yellow'), colored('人数', 'yellow'),
                            '还需₵', '还需人数',
                            '目标投入₵', '还需投入₵'),
                           output_format, disable_numparse=True
                           ), file=output)

        pydoc.pager(output.getvalue())

    if not in_initial and not initialized:
        click.echo("Nothing to show", err=True)
