import re
from typing import *

import click

from bgmd.api import person_work_voice_character
from bgmd.model import Person
from db import accounts as db_accounts
from tinygrail.api import batch_character_info, get_full_holding
from tinygrail.model import TICO
from tinygrail.player import Player


def parse_target(target_str):
    general_target = (0, 0)
    targets: Dict[int, Tuple[int, int]] = {}
    for small_target in target_str.split(","):
        t = re.compile(r"(?:(?P<cid>\d*)=)?(?P<hold>\d*)/(?P<tower>\d*)").fullmatch(small_target)
        if t is None:
            print("Bad target value. Syntax: [cid=]hold/tower")
            raise click.exceptions.Exit(10)
        t = t.groupdict()
        if t['cid'] in {None, ''}:
            general_target = int(t['hold']), int(t['tower'])
        else:
            targets[int(t['cid'])] = int(t['hold']), int(t['tower'])
    return targets, general_target


@click.command()
@click.argument('person_id', type=int)
@click.option('--account', default=None)
@click.option('--target', type=str)
def check_cv(person_id, account, target):
    cv = Person(id=person_id)
    cv_characters: List[int] = sorted(c.id for c in person_work_voice_character(cv))
    if account is None and target is None:
        for cv_character in cv_characters:
            print(cv_character)
        return
    targets, default_target = parse_target(target)

    players_dicts = db_accounts.retrieve(account)
    if len(players_dicts) == 0:
        print("No such account!")
        raise click.exceptions.Exit(1)
    player = Player(identity=players_dicts[0]['tinygrail_identity'])

    characters = get_full_holding(player)
    checks = []
    for cid in sorted(cv_characters):
        if cid in characters:
            th, tt = targets.get(cid, default_target)
            ch, ct = characters[cid]
            if not (ch >= th and ct >= tt):
                click.echo(f"#{cid:<5} | target: {th}/{tt}, actual: {ch}/{ct}")
        else:
            th, tt = targets.get(cid, default_target)
            if (th, tt) != (0, 0):
                checks.append(cid)
    if checks:
        for c in batch_character_info(player, checks):
            if isinstance(c, TICO):
                click.echo(f"#{c.character_id:<5} | ICO")
            else:
                click.echo(f"#{c.character_id:<5} | Available")
