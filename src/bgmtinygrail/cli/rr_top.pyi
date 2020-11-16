from typing import Optional

from ..tinygrail import Player, BigC


def calculate_target_extra(target_rank: int) -> int: ...


# def wrap_do_auction(big_c: BigC, name: str) -> Callable[[float, int, bool], None]: ...


# noinspection PyPep8Naming
class wrap_do_auction:
    def __init__(self, big_c: BigC, name: str): ...

    def __call__(self, price: float, amount: int, allow_dec: bool): ...


def rr_top(
        catcher: Player,
        thrower: Player,
        cid: int,
        target_rank: int,
        upper_limit: int
): ...


def rr_top_catch(
        catcher: Player,
        cid: int,
        catch_amount: Optional[int],
        target_rank: Optional[int],
        catch_price: float
): ...


def rr_top_throw(thrower: Player, cid: int, target_rank: int): ...
