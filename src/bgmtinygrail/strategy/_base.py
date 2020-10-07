import logging
from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import *

from ..tinygrail.bigc import BigC
from ..tinygrail.model import TBid, TAsk
from ..tinygrail.player import Player

logger = logging.getLogger('strategy')


class Strategy(Enum):
    NONE = 0
    IGNORE = 1
    CLOSE_OUT = 2
    BALANCE = 3
    SELF_SERVICE = 4
    BUY_IN = 5
    SHOW_GRACE = 6
    USER_DEFINED = 100


@lru_cache()
def _big_c(player, cid):
    return BigC(player, cid)


class ABCCharaStrategy(ABC):
    cid: int
    player: Player
    trader: 'trader.ABCTrader'
    kwargs: Dict[str, Any]
    strategy: ClassVar[Strategy] = Strategy.NONE

    def __init__(self, player, cid, *,
                 trader: 'trader.ABCTrader' = None, trader_cls: 'Type[trader.ABCTrader]' = None,
                 **kwargs):
        assert hasattr(player, 'session'), ValueError
        assert isinstance(cid, int), ValueError
        self.player = player
        if not (bool(trader) ^ callable(trader_cls)):
            raise TypeError("strategies must be inited with either of these keyword arguments: "
                            "'trader', 'trader_cls'") from None
        self.trader = trader or trader_cls(player)
        self.cid = cid
        self.kwargs = kwargs
        self.__post_init__()

    def __post_init__(self):
        pass

    def _transact(self, strategy_class: 'Type[ABCCharaStrategy]' = None, **kwargs):
        strategy_class = strategy_class or self.__class__
        return strategy_class(self.player, self.cid, trader=self.trader, **kwargs)

    @property
    def big_c(self):
        res = _big_c(self.player, self.cid)
        res.update()
        return res

    @property
    def _fundamental(self):
        return round(self.big_c.rate / self.trader.internal_rate, 2)

    @property
    def _exchange_price(self):
        return max(self.big_c.initial_price_rounded, self._fundamental)

    @abstractmethod
    def transition(self) -> 'ABCCharaStrategy':
        return self

    @abstractmethod
    def output(self):
        pass

    def _fast_forward(self, price=None):
        price = price or self._exchange_price
        logger.debug(f"fast forward #{self.cid:<5} | {price}")
        big_c = self.big_c
        amount = 100
        big_c.ensure_bids([], force_updates='after')
        while not big_c.bids:
            big_c.ensure_bids([TBid(Price=price, Amount=amount)], force_updates='after')
            amount *= 2
        big_c.ensure_bids([], force_updates='after')

    def _fast_seller(self, amount=None, low=10, high=100000):
        if amount is None:
            amount = self.big_c.amount
        logger.debug(f"fast seller #{self.cid:<5} | ({low}-{high}) / {amount}")
        big_c = self.big_c
        big_c.ensure_bids([], force_updates='before')
        big_c.ensure_asks([], force_updates='after')
        while amount:
            pin = round(0.618 * high + 0.382 * low, 2)
            if pin == high or pin == low:
                break
            big_c.ensure_asks([TAsk(Price=pin, Amount=1)], force_updates='after')
            if big_c.asks:
                big_c.ensure_asks([], force_updates='after')
                high = pin
            else:
                low = pin
                amount -= 1
        if amount:
            big_c.ensure_asks([TAsk(Price=low, Amount=amount)], force_updates='after')

    def _output_balanced(self):
        exchange_price = self._exchange_price
        big_c = self.big_c
        big_c.update_user_character(ignore_throttle=True)
        if big_c.total_holding:
            big_c.ensure_asks([TAsk(Price=exchange_price, Amount=big_c.total_holding)])
        big_c.ensure_bids([TBid(Price=exchange_price, Amount=100)], force_updates='after')
