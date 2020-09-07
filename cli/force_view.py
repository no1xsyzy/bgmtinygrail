from tinygrail.bigc import BigC
from tinygrail.model import TBid

from ._base import *


@click.command()
@click.argument("player_name", type=TG_PLAYER)
@click.argument("character_ids", type=int, nargs=-1)
def force_view(player_name, character_ids):
    for cid in character_ids:
        big_c = BigC(player_name, cid)
        big_c.create_bid(TBid(Price=2, Amount=2))
