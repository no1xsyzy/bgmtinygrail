from .api import *
from datetime import datetime, timedelta

logger = logging.getLogger('big_c')

_INTERNAL_RATE = 0.1

_USER_CHARACTER_THROTTLE_DELTA = timedelta(seconds=2)
_CHARACTER_INFO_THROTTLE_DELTA = timedelta(seconds=2)
_CHARTS_THROTTLE_DELTA = timedelta(seconds=2)


class BigC:
    # user character
    player: Player
    character: int
    bids: List[TBid]
    asks: List[TAsk]
    amount: int
    total_holding: int
    # character info
    name: str
    is_ICO: bool
    is_on_market: bool
    ICO_begin: Optional[datetime]
    ICO_end: Optional[datetime]
    ICO_total_backed: Optional[float]
    ICO_my_backed: Optional[float]
    ICO_users: Optional[int]
    global_holding: Optional[int]
    current_price: Optional[float]
    last_order: Optional[datetime]
    last_deal: Optional[datetime]
    global_sacrifices: Optional[int]
    rate: Optional[float]
    price: Optional[float]
    # charts
    charts: List[TChartum]

    _uc_update: Optional[datetime]
    _ci_update: Optional[datetime]
    _ch_update: Optional[datetime]

    def __init__(self, player, character):
        self.player = player
        self.character = character
        self._uc_update = datetime(1, 1, 1)
        self._ci_update = datetime(1, 1, 1)
        self._ch_update = datetime(1, 1, 1)
        self.update(ignore_throttle=True)

    def update(self, **kwargs):
        self._update_user_character(**kwargs)
        self._update_character_info(**kwargs)
        self._update_charts(**kwargs)

    def _update_user_character(self, ignore_throttle=False):
        if ignore_throttle or self._uc_update > datetime.now():
            return
        uc = user_character(self.player, self.character).value
        self.bids = uc.bids
        self.asks = uc.asks
        self.amount = uc.amount
        self.total_holding = uc.total_holding
        self._uc_update = datetime.now() + _USER_CHARACTER_THROTTLE_DELTA

    def _update_character_info(self, ignore_throttle=False):
        if ignore_throttle or self._ci_update > datetime.now():
            return
        ci = character_info(self.player, self.character).value
        self.name = ci.name
        if isinstance(ci, TICO):
            self.is_ICO = True
            self.is_on_market = False
            self.ICO_begin = ci.begin
            self.ICO_end = ci.end
            self.ICO_total_backed = ci.total
            self.ICO_my_backed = get_my_ico(self.player, ci.id).amount
            self.ICO_users = ci.users
        elif isinstance(ci, TCharacter):
            self.is_ICO = False
            self.is_on_market = True
            self.global_holding = ci.total
            self.current_price = ci.current
            self.last_order = ci.last_order
            self.last_deal = ci.last_deal
            self.global_sacrifices = ci.sacrifices
            self.rate = ci.rate
            self.price = ci.price
        self._ci_update = datetime.now() + _CHARACTER_INFO_THROTTLE_DELTA

    def _update_charts(self, ignore_throttle=False):
        if ignore_throttle or self._ch_update > datetime.now():
            return
        cc = chara_charts(self.player, self.character)
        self.charts = cc
        self._ch_update = datetime.now() + _CHARTS_THROTTLE_DELTA

    @property
    def current_price_rounded(self):
        return round(self.current_price, 2)

    @property
    def initial_price(self):
        return self.charts[0].price

    @property
    def initial_price_rounded(self):
        return round(self.initial_price, 2)

    @property
    def fundamental(self):
        return self.rate / _INTERNAL_RATE

    @property
    def fundamental_rounded(self):
        return round(self.fundamental, 2)

    def create_bid(self, bid: TBid):
        return create_bid(self.player, self.character, bid)

    def create_ask(self, ask: TAsk):
        return create_ask(self.player, self.character, ask)

    def cancel_bid(self, bid: TBid):
        return cancel_bid(self.player, bid)

    def cancel_ask(self, ask: TAsk):
        return cancel_ask(self.player, ask)

    def ensure_bids(self, bids: List[TBid]):
        self._update_user_character()
        now_bids = self.bids
        now_bids = sorted(now_bids)
        bids = sorted(bids)
        while now_bids and bids:
            if now_bids[0] < bids[0]:
                logger.info(f"Cancel: {now_bids[0]!r}")
                self.cancel_bid(now_bids.pop(0))
            elif now_bids[0] > bids[0]:
                logger.info(f"Create: {bids[0]!r}")
                self.create_bid(bids.pop(0))
            else:
                logger.info(f"Equals: {now_bids[0]!r}")
                now_bids.pop(0)
                bids.pop(0)

        for now_bid in now_bids:
            self.cancel_bid(now_bid)

        for bid in bids:
            self.create_bid(bid)

    def ensure_asks(self, asks: List[TAsk]):
        self._update_user_character()
        now_asks = self.asks
        now_asks = sorted(now_asks)
        asks = sorted(asks)
        while now_asks and asks:
            if now_asks[0] < asks[0]:
                logger.info(f"Cancel: {now_asks[0]!r}")
                self.cancel_ask(now_asks.pop(0))
            elif now_asks[0] > asks[0]:
                logger.info(f"Create: {asks[0]!r}")
                self.create_ask(asks.pop(0))
            else:
                logger.info(f"Equals: {now_asks[0]!r}")
                now_asks.pop(0)
                asks.pop(0)

        for now_ask in now_asks:
            self.cancel_ask(now_ask)

        for ask in asks:
            self.create_ask(ask)
