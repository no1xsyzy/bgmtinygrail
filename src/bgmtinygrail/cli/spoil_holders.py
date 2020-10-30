import click

from ._base import TG_PLAYER
from ..tinygrail.api import spoil_holders as api_spoil_holders
from ..tinygrail.model import TMinimalUserCharacter, TAuction
from ..tinygrail.player import Player


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('cid', type=int)
def spoil_holders(player: Player, cid: int):
    holders = api_spoil_holders(player, cid)
    auction = None
    for muc, holder in holders:
        if isinstance(muc, TMinimalUserCharacter):
            click.echo(f"{holder.nickname}({holder.name}) - {muc.total}/{muc.sacrifices}")
        elif isinstance(muc, TAuction):
            auction = muc
    if auction is not None:
        click.echo(f"Totally {auction.total}, {auction.auction_users} user(s) raced for {auction.auction_total} stocks")
