from .api import *
from datetime import datetime

logger = logging.getLogger('big_c')


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

    def __init__(self, player, character):
        self.player = player
        self.character = character
        self.update()

    def update(self):
        self._update_user_character()
        self._update_character_info()
        self._update_charts()

    def _update_user_character(self):
        uc = user_character(self.player, self.character).value
        self.bids = uc.bids
        self.asks = uc.asks
        self.amount = uc.amount
        self.total_holding = uc.total_holding

    def _update_character_info(self):
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

    def _update_charts(self):
        cc = chara_charts(self.player, self.character)
        self.charts = cc

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
        return self.rate / 0.12

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
                cancel_bid(self.player, now_bids.pop(0))
            elif now_bids[0] > bids[0]:
                logger.info(f"Create: {bids[0]!r}")
                create_bid(self.player, self.character, bids.pop(0))
            else:
                logger.info(f"Equals: {now_bids[0]!r}")
                now_bids.pop(0)
                bids.pop(0)

        for now_bid in now_bids:
            cancel_bid(self.player, now_bid)

        for bid in bids:
            create_bid(self.player, self.character, bid)

    def ensure_asks(self, asks: List[TAsk]):
        self._update_user_character()
        now_asks = self.asks
        now_asks = sorted(now_asks)
        asks = sorted(asks)
        while now_asks and asks:
            if now_asks[0] < asks[0]:
                logger.info(f"Cancel: {now_asks[0]!r}")
                cancel_ask(self.player, now_asks.pop(0))
            elif now_asks[0] > asks[0]:
                logger.info(f"Create: {asks[0]!r}")
                create_ask(self.player, self.character, asks.pop(0))
            else:
                logger.info(f"Equals: {now_asks[0]!r}")
                now_asks.pop(0)
                asks.pop(0)

        for now_ask in now_asks:
            cancel_ask(self.player, now_ask)

        for ask in asks:
            create_ask(self.player, self.character, ask)
