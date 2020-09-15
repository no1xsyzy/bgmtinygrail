from typing import *

import click

from bgmd.api import person_work_voice_character
from bgmd.model import Person
from tinygrail.api import batch_character_info, get_full_holding
from tinygrail.model import TICO
from tinygrail.player import Player
from ._base import TG_PLAYER
from ._helpers import parse_target


@click.command()
@click.argument('person_id', type=int)
@click.option('--player', type=TG_PLAYER, default=None)
@click.option('--target', type=str)
def check_cv(person_id, player: Player, target: str):
    if player is None and target is None:
        cv = Person(id=person_id)
        cv_characters: List[int] = sorted(c.id for c in person_work_voice_character(cv))
        for cv_character in cv_characters:
            print(cv_character)
        return

    target_strings = target.split(",")
    for i, ts in enumerate(target_strings):
        if "=" not in ts[1:]:
            target_strings[i] = f"cv/{person_id}={ts.lstrip('=')}"
            break
    targets = parse_target(target_strings)

    characters = get_full_holding(player)
    checks = []
    for cid, (th, tt) in targets.items():
        if cid in characters:
            ch, ct = characters[cid]
            if not (ch >= th and ct >= tt):
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
