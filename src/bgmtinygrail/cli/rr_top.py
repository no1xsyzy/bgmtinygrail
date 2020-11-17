from datetime import datetime
from math import ceil, floor

import click

from ._base import TG_PLAYER
from ..tinygrail.api import top_week, character_auction, my_auctions
from ..tinygrail.bigc import BigC


def calculate_target_extra(target_rank):
    if target_rank in range(1, 4):
        return 2000 - 500 * (target_rank - 1)
    if target_rank in range(4, 13):
        return 500 - 50 * (target_rank - 4)
    raise ValueError


def wrap_do_auction(big_c, name):
    def wrapped(price, amount, allow_dec):
        print(f"{name}.do_auction({price=}, {amount=}, {allow_dec=})  # {price*amount=}")
        big_c.do_auction(price, amount, allow_dec=allow_dec)

    return wrapped


@click.command()
@click.argument('catcher', type=TG_PLAYER)
@click.argument('thrower', type=TG_PLAYER)
@click.argument('cid', type=int)
@click.argument('target_rank', type=click.IntRange(1, 12))
def rr_top(catcher, thrower, cid, target_rank):
    if target_rank in range(1, 4):
        click.confirm(f"You are requesting rank {target_rank}, "
                      "which will cause loss of used cc's, sure?", abort=True)
    target_extra = calculate_target_extra(target_rank)

    now_top_week = top_week()

    def get_rank():
        nonlocal now_top_week
        now_top_week = top_week()
        try:
            return next(i for i, e in enumerate(now_top_week) if e.character_id == cid) + 1
        except StopIteration:
            return 10000

    catcher_bc = BigC(catcher, cid)
    catcher_bc_do_auction = wrap_do_auction(catcher_bc, "catcher_bc")

    thrower_bc = BigC(thrower, cid)
    thrower_bc_do_auction = wrap_do_auction(thrower_bc, "thrower_bc")

    allow_dec = datetime.today().isoweekday() != 6

    ca = character_auction(catcher, cid)

    total_can_get = ca.amount + target_extra
    base_price = ca.price
    normalized_base_price = ceil(base_price * 100) * 0.01

    if not my_auctions(thrower, [cid]):
        thrower_bc.do_auction(normalized_base_price, 1)
    if not my_auctions(catcher, [cid]):
        catcher_bc.do_auction(normalized_base_price, 1)

    catch_price = max(normalized_base_price + 0.01, catcher_bc.my_auction_price)

    if allow_dec:
        step = 1024
        catcher_bc_do_auction(catch_price, total_can_get, allow_dec)
    else:
        step = 1

    reg = None

    while (rank := get_rank()) != target_rank:
        if rank > 100:
            current_total_value = thrower_bc.my_auction_total_value
            ca = character_auction(thrower, cid)  # should be fetched again
            target_delta_value = (min(tw.score_1 for tw in now_top_week)) / ca.auction_users
            thrower_bc_do_auction(
                normalized_base_price,
                floor((current_total_value + target_delta_value) / normalized_base_price) + 1,
                allow_dec
            )
        elif rank > target_rank:
            if reg is True:
                step = (step + 1) // 2
            reg = False
            print(f"{rank} == rank > target_rank == {target_rank}")
            if catcher_bc.my_auction_amount < total_can_get:
                catcher_bc_do_auction(catch_price, catcher_bc.my_auction_amount + 1, allow_dec)
            else:
                current_total_value = thrower_bc.my_auction_total_value
                print(f"{current_total_value=}")
                target_delta_value = now_top_week[target_rank - 1].score_2 - now_top_week[rank - 1].score_2
                print(f"{target_delta_value=}")
                thrower_bc_do_auction(
                    normalized_base_price,
                    floor((current_total_value + target_delta_value) / normalized_base_price) + 1,
                    allow_dec
                )
        else:  # rank < target_rank
            if reg is False:
                step = (step + 1) // 2
            reg = True
            print(f"{rank} == rank < target_rank == {target_rank}")
            if catcher_bc.my_auction_amount > total_can_get:
                catcher_bc_do_auction(catch_price, catcher_bc.my_auction_amount - 1, allow_dec)
            else:
                thrower_bc_do_auction(
                    normalized_base_price,
                    ceil(thrower_bc.my_auction_total_value / normalized_base_price) - step,
                    allow_dec
                )
    else:
        print(f"{rank} == rank == target_rank == {target_rank}")


@click.command()
@click.argument('catcher', type=TG_PLAYER)
@click.argument('cid', type=int)
@click.option('-p', '--catch-price', type=float, default=None)
@click.option('-n', '--catch-amount', type=int, default=None)
@click.option('-t', '--target-rank', type=click.IntRange(1, 12), default=None)
def rr_top_catch(catcher, cid, catch_amount, target_rank, catch_price):
    if catch_amount is None and target_rank is None:
        raise ValueError
    if catch_price is None or catch_amount is None:
        ca = character_auction(catcher, cid)
        if catch_amount is None:
            assert target_rank is not None
            catch_amount = ca.amount + calculate_target_extra(target_rank)
        if catch_price is None:
            catch_price = ceil(ca.price * 100) * 0.01 + 0.01

    catcher_bc = BigC(catcher, cid)
    catcher_bc_do_auction = wrap_do_auction(catcher_bc, "catcher_bc")

    allow_dec = datetime.today().isoweekday() != 6

    catcher_bc_do_auction(catch_price, catch_amount, allow_dec)


@click.command()
@click.argument('thrower', type=TG_PLAYER)
@click.argument('cid', type=int)
@click.argument('target_rank', type=click.IntRange(1, 12))
def rr_top_throw(thrower, cid, target_rank):
    if target_rank in range(1, 4):
        click.confirm(f"You are requesting rank {target_rank}, "
                      "which will cause loss of used cc's, sure?", abort=True)

    now_top_week = top_week()

    def get_rank():
        nonlocal now_top_week
        now_top_week = top_week()
        try:
            return next(i for i, e in enumerate(now_top_week) if e.character_id == cid) + 1
        except StopIteration:
            return 10000

    thrower_bc = BigC(thrower, cid)
    thrower_bc_do_auction = wrap_do_auction(thrower_bc, "thrower_bc")

    ca = character_auction(thrower, cid)
    base_price = ca.price
    normalized_base_price = ceil(base_price * 100) * 0.01

    allow_dec = datetime.today().isoweekday() != 6

    if allow_dec:
        step = 1024
    else:
        step = 1

    if not my_auctions(thrower, [cid]):
        thrower_bc_do_auction(
            normalized_base_price,
            1,
            allow_dec
        )

    reg = None

    while (rank := get_rank()) != target_rank:
        if rank > 100:
            current_total_value = thrower_bc.my_auction_total_value
            ca = character_auction(thrower, cid)
            target_delta_value = (min(tw.score_1 for tw in now_top_week)) / ca.auction_users
            thrower_bc_do_auction(
                normalized_base_price,
                floor((current_total_value + target_delta_value) / normalized_base_price) + 1,
                allow_dec
            )
        elif rank > target_rank:
            if reg is True:
                step = (step + 1) // 2
            reg = False
            print(f"{rank} == rank > target_rank == {target_rank}")
            current_total_value = thrower_bc.my_auction_total_value
            print(f"{current_total_value=}")
            target_delta_value = now_top_week[target_rank - 1].score_2 - now_top_week[rank - 1].score_2
            print(f"{target_delta_value=}")
            thrower_bc_do_auction(
                normalized_base_price,
                floor((current_total_value + target_delta_value) / normalized_base_price) + 1,
                allow_dec
            )
        else:  # rank < target_rank
            if reg is False:
                step = (step + 1) // 2
            reg = True
            print(f"{rank} == rank < target_rank == {target_rank}")
            thrower_bc_do_auction(
                normalized_base_price,
                ceil(thrower_bc.my_auction_total_value / normalized_base_price) - step,
                allow_dec
            )
    else:
        print(f"{rank} == rank == target_rank == {target_rank}")
