from math import ceil, floor

import click

from ._base import TG_PLAYER
from ..tinygrail.api import top_week, character_auction, my_auctions
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

    now_top_week = top_week()

    def get_rank():
        nonlocal now_top_week
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

    if not my_auctions(thrower, [cid]):
        thrower_bc.do_auction(base_price, 1)
    if not my_auctions(catcher, [cid]):
        catcher_bc.do_auction(base_price, 1)

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
        if rank > 100:
            price = base_price
            current_total_value = thrower_bc.my_auction_total_value
            ca = character_auction(thrower, cid)
            target_delta_value = (min(tw.score_1 for tw in now_top_week)) / ca.auction_users
            amount = floor((current_total_value + target_delta_value) / base_price) + 1
            print(f"thrower_bc.do_auction({price=}, {amount=}, {allow_dec=})")
            thrower_bc.do_auction(price=price, amount=amount, allow_dec=allow_dec)
        elif rank > target_rank:
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
                current_total_value = thrower_bc.my_auction_total_value
                print(f"{current_total_value=}")
                target_delta_value = now_top_week[target_rank - 1].score_2 - now_top_week[rank - 1].score_2
                print(f"{target_delta_value=}")
                amount = floor((current_total_value + target_delta_value) / base_price) + 1
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
