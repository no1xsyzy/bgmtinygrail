import re
from typing import *

import click

from bgmd.api import person_work_voice_character
from bgmd.model import Person
from tinygrail.api import batch_character_info, get_full_holding
from tinygrail.model import TICO
from ._base import TG_PLAYER

PARSER_RE = re.compile(r"(?:(?P<cid>\d+)|cv/(?P<cv_id>\d+)) *= *(?P<hold>\d+)?(?:/(?P<tower>\d+))?")


def parse_target(targets: List[str]) -> Dict[int, Tuple[int, int]]:
    result: Dict[int, Tuple[int, int]] = {}
    for target in targets:
        t = PARSER_RE.fullmatch(target)
        if t is None:
            print(f"Bad target value `{target}`. Syntax: <cid> = <hold>/<tower>, cv/<cv_id> = <hold>/<tower>")
            raise click.exceptions.Exit(10)
        t = t.groupdict()
        if t['cid'] is not None:
            result[int(t['cid'])] = int(t['hold']), int(t['tower'])
        elif t['cv_id'] is not None:
            for cid in person_work_voice_character(Person(id=int(t['cv_id']))):
                result[cid.id] = int(t['hold']), int(t['tower'])
    return result


@click.command()
@click.option('--player', type=TG_PLAYER)
@click.option('--target', type=str)
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, target, show_exceeds):
    targets = parse_target(target.split(","))
    characters = get_full_holding(player)

    checks = []
    for cid, (th, tt) in targets.items():
        if cid in characters:
            ch, ct = characters[cid]
            if (not (ch >= th and ct >= tt)) or (show_exceeds and not (ch == th and ct == tt)):
                click.echo(f"#{cid:<5} | target: {th}/{tt}, actual: {ch}/{ct}")
        else:
            if (th, tt) != (0, 0):
                checks.append(cid)

    if checks:
        for c in batch_character_info(player, checks):
            if isinstance(c, TICO):
                click.echo(f"#{c.character_id:<5} | ICO")
            else:
                click.echo(f"#{c.character_id:<5} | Available")
