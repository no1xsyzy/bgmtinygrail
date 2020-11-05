from math import ceil, floor

import click

from ._base import TG_PLAYER
from ..tinygrail.api import top_week, character_auction
from ..tinygrail.bigc import BigC


@click.command()
@click.argument('catcher', type=TG_PLAYER)
@click.argument('thrower', type=TG_PLAYER)
@click.argument('cid', type=int)
@click.argument('target_rank', type=click.IntRange(1, 12))
def rr_top(catcher, thrower, cid, target_rank):
    target_extra = None
    if target_rank in range(1, 4):
        click.confirm(f"You are requesting rank {target_rank}, "
                      "which will cause loss of used cc's, sure?", abort=True)
        target_extra = 2000 - 500 * (target_rank - 1)
    if target_rank in range(4, 13):
        target_extra = 500 - 50 * (target_rank - 4)
    if target_extra is None:
        raise

    def get_rank():
        now_top_week = top_week()
        try:
            return next(i for i, e in enumerate(now_top_week) if e.character_id == cid) + 1
        except StopIteration:
            return 10000

    catcher_bc = BigC(catcher, cid)
    thrower_bc = BigC(thrower, cid)

    ca = character_auction(catcher, cid)

    total_can_get = ca.amount + target_extra
    base_price = ca.price

    from datetime import datetime

    allow_dec = datetime.today().isoweekday() != 6

    if allow_dec:
        step = 1024
        price = base_price + 0.01
        amount = total_can_get
        print(f"catcher_bc.do_auction({price=}, {amount=}, {allow_dec=})")
        catcher_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
    else:
        step = 1

    reg = None

    while (rank := get_rank()) != target_rank:
        if rank > target_rank:
            if reg is True:
                step = (step + 1) // 2
            reg = False
            print(f"({rank=}) > ({target_rank=})")
            if catcher_bc.my_auction_amount < total_can_get:
                price = base_price + 0.01
                amount = catcher_bc.my_auction_amount + 1
                print(f"catcher_bc.do_auction({price=}, {amount=}, {allow_dec=})")
                catcher_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
            else:
                price = base_price
                amount = floor(thrower_bc.my_auction_total_value / base_price) + step
                print(f"thrower_bc.do_auction({price=}, {amount=}, {allow_dec=})")
                thrower_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
        else:  # rank < target_rank
            if reg is False:
                step = (step + 1) // 2
            reg = True
            print(f"({rank=}) < ({target_rank=})")
            if catcher_bc.my_auction_amount > total_can_get:
                price = base_price + 0.01
                amount = catcher_bc.my_auction_amount - 1
                print(f"catcher_bc.do_auction({price=}, {amount=}, {allow_dec=})")
                catcher_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
            else:
                price = base_price
                amount = ceil(thrower_bc.my_auction_total_value / base_price) - step
                print(f"thrower_bc.do_auction({price=}, {amount=}, {allow_dec=})")
                thrower_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
