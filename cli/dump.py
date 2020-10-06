import click

from tinygrail.api import all_holding, user_temples
from tinygrail.player import Player
from ._base import TG_PLAYER


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.option('+temple/-temple')
@click.option('+holding/-holding')
def dump(player: Player, temple: bool, holding: bool):
    result = set()
    if holding:
        result.update(c.id for c in all_holding(player))
    if temple:
        result.update(temple.character_id for temple in user_temples(player))
    for c in sorted(result):
        print(c)
