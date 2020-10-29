import click

from ._base import TG_PLAYER
from ..tinygrail.api import spoil_holders as api_spoil_holders
from ..tinygrail.player import Player


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('cid', type=int)
def spoil_holders(player: Player, cid: int):
    holders = api_spoil_holders(player, cid)
    for muc, holder in holders:
        click.echo(f"{holder.nickname}({holder.name}) - {muc.total}/{muc.sacrifices}")
