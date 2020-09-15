import logging
from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import *

from tinygrail.api import get_initial_price, user_character, character_info
from tinygrail.bigc import BigC
from tinygrail.model import TAsk, TBid
from tinygrail.player import Player

logger = logging.getLogger('strategy')

__all__ = [
    'Strategy', 'ABCCharaStrategy',
    'IgnoreStrategy',
    'CloseOutStrategy',
    'BalanceStrategy',
    'SelfServiceStrategy',
    'BuyInStrategy',
    'all_strategies'
]


class Strategy(Enum):
    NONE = 0
    IGNORE = 1
    CLOSE_OUT = 2
    BALANCE = 3
    SELF_SERVICE = 4
    BUY_IN = 5
    USER_DEFINED = 100


@lru_cache()
def _big_c(player, cid):
    return BigC(player, cid)


class ABCCharaStrategy(ABC):
    cid: int
    player: Player
    strategy: ClassVar[Strategy] = Strategy.NONE

    def __init__(self, player, cid, **kwargs):
        assert hasattr(player, 'session'), ValueError
        assert isinstance(cid, int), ValueError
        self.player = player
        self.cid = cid
        self.kwargs = kwargs

    def user_character(self):
        return user_character(self.player, self.cid)

    def character_info(self):
        return character_info(self.player, self.cid)

    def current_price(self):
        return round(self.character_info().current, 2)

    def initial_price(self):
        return round(get_initial_price(self.player, self.cid), 2)

    @property
    def exchange_price(self):
        return max(self.big_c.initial_price_rounded, self.big_c.fundamental_rounded)

    @property
    @lru_cache(maxsize=1000)
    def big_c(self):
        return _big_c(self.player, self.cid)

    def ensure_bids(self, bids: List[TBid]):
        self.big_c.ensure_bids(bids)

    def ensure_asks(self, asks: List[TAsk]):
        self.big_c.ensure_asks(asks)

    @abstractmethod
    def transition(self) -> 'ABCCharaStrategy':
        return self

    @abstractmethod
    def output(self):
        pass


class IgnoreStrategy(ABCCharaStrategy):
    strategy = Strategy.IGNORE

    def transition(self):
        if self.big_c.total_holding > 0:
            if self.big_c.current_price <= self.exchange_price:
                return BalanceStrategy(self.player, self.cid)
            return CloseOutStrategy(self.player, self.cid)
        return self

    def output(self):
        self.ensure_asks([])
        self.ensure_bids([])


class CloseOutStrategy(ABCCharaStrategy):
    strategy = Strategy.CLOSE_OUT

    def transition(self):
        uc = self.user_character()
        if uc.total_holding == 0:
            return IgnoreStrategy(self.player, self.cid)
        else:
            return BalanceStrategy(self.player, self.cid)

    def output(self):
        self.ensure_asks([TAsk(Price=self.exchange_price, Amount=self.user_character().total_holding)])
        self.ensure_bids([])


class BalanceStrategy(ABCCharaStrategy):
    strategy = Strategy.BALANCE

    @property
    def bid_amount(self):
        return self.kwargs.get('bid_amount', 100)

    def transition(self):
        uc = self.user_character()
        if uc.total_holding == 0:
            return IgnoreStrategy(self.player, self.cid)
        if not uc.bids:
            return BalanceStrategy(self.player, self.cid, bid_amount=self.bid_amount * 2)
        if self.bid_amount > 100:
            return BalanceStrategy(self.player, self.cid)
        return self

    def output(self):
        self.ensure_asks([TAsk(Price=self.exchange_price, Amount=self.user_character().total_holding)])
        self.ensure_bids([TBid(Price=self.exchange_price, Amount=self.bid_amount)])


class SelfServiceStrategy(ABCCharaStrategy):
    strategy = Strategy.SELF_SERVICE

    def transition(self):
        return self

    def output(self):
        pass


class BuyInStrategy(ABCCharaStrategy):
    strategy = Strategy.BUY_IN

    def transition(self):
        return self

    def output(self):
        self.ensure_asks([])
        self.ensure_bids([TBid(Price=self.exchange_price, Amount=100)])


all_strategies: Dict[Strategy, Type[ABCCharaStrategy]] = {
    Strategy.IGNORE: IgnoreStrategy,
    Strategy.CLOSE_OUT: CloseOutStrategy,
    Strategy.BALANCE: BalanceStrategy,
    Strategy.SELF_SERVICE: SelfServiceStrategy,
    Strategy.BUY_IN: BuyInStrategy,
}
