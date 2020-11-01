import click

from ._base import TG_PLAYER
from ..tinygrail.bigc import BigC
from ..tinygrail.model import TAsk, TBid
from ..tinygrail.player import Player


@click.command()
@click.argument('holder_player', type=TG_PLAYER)
@click.argument('helper_player', type=TG_PLAYER)
@click.argument('cid', type=int)
@click.argument('price', type=float)
def spoil_highest_bid(holder_player: Player, helper_player: Player, cid: int, price: float):
    holder = BigC(holder_player, cid)
    helper = BigC(helper_player, cid)
    if holder.my_asks and holder.my_bids:
        max_bid_price = max(bid.price for bid in holder.my_bids)
        min_ask_price = min(ask.price for ask in holder.my_asks)
        if min_ask_price <= max_bid_price:
            # already in balance
            click.echo(f"already in balance: {min_ask_price} <= {max_bid_price}")
            return
        else:
            if min_ask_price < price:
                price = min_ask_price
    elif holder.my_asks:  # and not holder.bids
        min_ask_price = min(ask.price for ask in holder.my_asks)
        if min_ask_price < price:
            price = min_ask_price
    elif holder.my_bids:  # and not holder.asks
        pass
    else:
        pass

    if helper.total_holding == 0:
        # convey 1 stock at price
        holder.create_ask(TAsk(Price=price, Amount=1))
        helper.create_bid(TBid(Price=price, Amount=1))
    if helper.total_holding == 0:
        # convey failure
        click.echo(f"conveying failure at price {price}, highest_bid is higher than it")
        return

    latest_id = max(bid_history.id for bid_history in holder.my_bid_history)

    holder.create_bid(TBid(Price=price, Amount=1, Type=1))
    helper.create_ask(TAsk(Price=2, Amount=1))

    cat_price = min(bid_history.price for bid_history in holder.my_bid_history if bid_history.id > latest_id)
    click.echo(f"checked: {cat_price}")
