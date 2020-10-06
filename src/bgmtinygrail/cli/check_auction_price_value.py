import click

from ._base import TG_PLAYER
from ..tinygrail.api import *


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def pv(player, cid) -> Tuple[int, str, float]:
    price = character_auction(player, cid).price
    chara_info = character_info(player, cid)
    assert isinstance(chara_info, TCharacter)
    value = chara_info.rate
    return chara_info.character_id, chara_info.name, value / price


@click.command()
@click.argument("player_name", type=TG_PLAYER)
def check_auction_price_value(player_name):
    result = []

    all_holdings = all_holding_ids(player_name)

    for n, cid in enumerate(all_holdings):
        print(f"fetching {n + 1}/{len(all_holdings)}: {cid}", end="\r")
        r = pv(player_name, cid)
        result.append(r)

    result = sorted(result, key=lambda t: t[2])

    for tup in result:
        print(*tup)
