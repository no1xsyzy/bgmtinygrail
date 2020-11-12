from typing import overload

from ..tinygrail import Player


def rr_top(
        catcher: Player,
        thrower: Player,
        cid: int,
        target_rank: int,
        upper_limit: int
): ...


@overload
def rr_top_catch(
        catcher: Player,
        cid: int,
        n: None,
        target_rank: int,
        catch_price: float
): ...


@overload
def rr_top_catch(
        catcher: Player,
        cid: int,
        n: int,
        target_rank: None,
        catch_price: float
): ...


def rr_top_throw(thrower: Player, cid: int, target_rank: int): ...
