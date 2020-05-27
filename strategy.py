from abc import ABC, abstractmethod
from enum import Enum

from tinygrail.api import *

logger = logging.getLogger('strategy')


class Strategy(Enum):
    NONE = 0
    IGNORE = 1
    CLOSE_OUT = 2
    BALANCE = 3
    SELF_SERVICE = 4
    BUY_IN = 5
    USER_DEFINED = 100


class ABCCharaStrategy(ABC):
    cid: int
    player: Player
    strategy: ClassVar[Strategy] = Strategy.NONE

    def __init__(self, player, cid, **kwargs):
        self.player = player
        self.cid = cid
        self.kwargs = kwargs

    def user_character(self):
        return user_character(self.player, self.cid).value

    def character_info(self):
        return character_info(self.player, self.cid).value

    def current_price(self):
        return round(self.character_info().current, 2)

    def initial_price(self):
        return round(get_initial_price(self.player, self.cid), 2)

    def ensure_bids(self, bids: List[TBid]):
        now_bids = self.user_character().bids
        now_bids = sorted(now_bids)
        bids = sorted(bids)
        while now_bids and bids:
            if now_bids[0] < bids[0]:
                logger.info(f"Cancel: {now_bids[0]!r}")
                cancel_bid(self.player, now_bids.pop(0))
            elif now_bids[0] > bids[0]:
                logger.info(f"Create: {bids[0]!r}")
                create_bid(self.player, self.cid, bids.pop(0))
            else:
                logger.info(f"Equals: {now_bids[0]!r}")
                now_bids.pop(0)
                bids.pop(0)

        for now_bid in now_bids:
            cancel_bid(self.player, now_bid)

        for bid in bids:
            create_bid(self.player, self.cid, bid)

    def ensure_asks(self, asks: List[TAsk]):
        now_asks = self.user_character().asks
        now_asks = sorted(now_asks)
        asks = sorted(asks)
        while now_asks and asks:
            if now_asks[0] < asks[0]:
                logger.info(f"Cancel: {now_asks[0]!r}")
                cancel_ask(self.player, now_asks.pop(0))
            elif now_asks[0] > asks[0]:
                logger.info(f"Create: {asks[0]!r}")
                create_ask(self.player, self.cid, asks.pop(0))
            else:
                logger.info(f"Equals: {now_asks[0]!r}")
                now_asks.pop(0)
                asks.pop(0)

        for now_ask in now_asks:
            cancel_ask(self.player, now_ask)

        for ask in asks:
            create_ask(self.player, self.cid, ask)

    @abstractmethod
    def transition(self) -> 'ABCCharaStrategy':
        return self

    @abstractmethod
    def output(self):
        pass


class IgnoreStrategy(ABCCharaStrategy):
    strategy = Strategy.IGNORE

    def transition(self):
        uc = self.user_character()
        current_price = self.current_price()
        initial_price = self.initial_price()
        logger.debug(f"{uc.total_holding=}, {current_price=}, {initial_price=}")
        if uc.total_holding > 0:
            if current_price <= initial_price:
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
        elif self.current_price() <= self.initial_price():
            return BalanceStrategy(self.player, self.cid)
        return self

    def output(self):
        self.ensure_asks([TAsk(self.initial_price(), self.user_character().total_holding)])
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
            return BalanceStrategy(self.player, self.cid, bid_amount=self.bid_amount*2)
        if self.bid_amount > 100:
            return BalanceStrategy(self.player, self.cid)
        return self

    def output(self):
        initial_price = self.initial_price()
        self.ensure_asks([TAsk(initial_price, self.user_character().total_holding)])
        self.ensure_bids([TBid(initial_price, self.bid_amount)])


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
        self.ensure_bids([TBid(self.initial_price(), 100)])


all_strategies: Dict[Strategy, Type[ABCCharaStrategy]] = {
    Strategy.IGNORE: IgnoreStrategy,
    Strategy.CLOSE_OUT: CloseOutStrategy,
    Strategy.BALANCE: BalanceStrategy,
    Strategy.SELF_SERVICE: SelfServiceStrategy,
    Strategy.BUY_IN: BuyInStrategy,
}
