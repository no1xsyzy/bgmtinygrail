from warnings import warn

from .api import *
from .refresher_matrix import *

logger = logging.getLogger('big_c')

_INTERNAL_RATE = 0.1

_USER_CHARACTER_THROTTLE_DELTA = timedelta(seconds=2)
_CHARACTER_INFO_THROTTLE_DELTA = timedelta(seconds=2)
_CHARTS_THROTTLE_DELTA = timedelta(seconds=2)
_DEPTH_THROTTLE_DELTA = timedelta(seconds=2)


class BigC:
    # user character
    player: Player
    character: int
    refresh_matrix: RefreshMatrix

    _user_character: TUserCharacter
    _character_info: Union[TCharacter, TICO]
    _my_ico: Optional[TMyICO]
    _charts: List[TChartum]
    _depth: TDepth

    def __init__(self, player: Player, character: int):
        self.player = player
        self.character = character
        self.refresh_matrix = RefreshMatrix([
            'my_asks', 'my_bids', 'amount', 'user_character',
            'ico_or_character', 'ico', 'character', 'my_ico',
            'charts', 'all_asks', 'all_bids',
        ])
        self.refresh_matrix.batch_register([
            ('my_asks', self.update_user_character),
            ('my_bids', self.update_user_character),
            ('amount', self.update_user_character),
            ('user_character', self.update_user_character),
            ('ico_or_character', self.update_character_info),
            ('ico', self.update_character_info_ico_only),
            ('character', self.update_character_info_on_market_only),
            ('my_ico', self.update_my_ico),
            ('charts', self.update_charts),
            ('all_asks', self.update_depth),
            ('all_bids', self.update_depth),
        ])
        self.refresh_matrix.interval['charts'] = timedelta(days=1)

    def invalidates(self, *tokens: Token):
        self.refresh_matrix.invalidates(*tokens)

    def refreshes(self, *tokens: Token):
        self.refresh_matrix.refreshes(*tokens)

    def update(self, **kwargs):
        if 'ignore_throttle' in kwargs:
            warn(DeprecationWarning("ignore_throttle is deprecated"))
        self.update_user_character()
        self.update_character_info()
        self.update_charts()
        self.update_depth()

    def update_user_character(self, **kwargs):
        if 'ignore_throttle' in kwargs:
            warn(DeprecationWarning("ignore_throttle is deprecated"))
        self._user_character = user_character(self.player, self.character)

    def update_character_info(self, **kwargs):
        if 'ignore_throttle' in kwargs:
            warn(DeprecationWarning("ignore_throttle is deprecated"))
        self._character_info = character_info(self.player, self.character)

    def update_character_info_ico_only(self):
        self.refreshes('ico_or_character')
        if not self.is_ico:
            raise ValueError(f"cid={self.character} is not in ICO")

    def update_my_ico(self):
        self.refreshes('ico')
        self._my_ico = get_my_ico(self.player, self.ico_id)

    def update_character_info_on_market_only(self):
        self.refreshes('ico_or_character')
        if not self.is_on_market:
            raise ValueError(f"cid={self.character} is not on market")

    def update_charts(self, **kwargs):
        if 'ignore_throttle' in kwargs:
            warn(DeprecationWarning("ignore_throttle is deprecated"))
        self._charts = chara_charts(self.player, self.character)

    def update_depth(self, **kwargs):
        if 'ignore_throttle' in kwargs:
            warn(DeprecationWarning("ignore_throttle is deprecated"))
        self._depth = depth(self.player, self.character)

    @property
    def current_price_rounded(self):
        return round(self.current_price, 2)

    @property
    def initial_price(self):
        return self.charts[0].begin

    @property
    def initial_price_rounded(self):
        return round(self.initial_price, 2)

    @property
    def fundamental(self):
        self.update_character_info()
        return self.rate / _INTERNAL_RATE

    @property
    def fundamental_rounded(self):
        return round(self.fundamental, 2)

    @property
    def total_holding(self):
        """Deprecated: ambiguous name"""
        warn(DeprecationWarning("ambiguous name 'total_holding', use 'my_holding' instead"))
        return self.amount + sum(ask.amount for ask in self.my_asks)

    @property
    def my_holding(self):
        return self.amount + sum(ask.amount for ask in self.my_asks)

    def create_bid(self, bid: TBid, **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        self.invalidates('my_bids', 'all_bids', 'amount')
        result = create_bid(self.player, self.character, bid)
        return result

    def create_ask(self, ask: TAsk, **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        self.invalidates('my_asks', 'all_asks', 'amount')
        result = create_ask(self.player, self.character, ask)
        return result

    def cancel_bid(self, bid: TBid, **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        self.invalidates('my_bids', 'all_bids', 'amount')
        result = cancel_bid(self.player, bid)
        return result

    def cancel_ask(self, ask: TAsk, **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        self.invalidates('my_asks', 'all_asks', 'amount')
        result = cancel_ask(self.player, ask)
        return result

    def ensure_bids(self, bids: List[TBid], **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        now_bids = self.my_bids
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

    def ensure_asks(self, asks: List[TAsk], **kwargs):
        if 'force_updates' in kwargs:
            warn(DeprecationWarning("force_updates is deprecated"))
        now_asks = self.my_asks
        now_asks = sorted(now_asks)
        asks = sorted(asks)
        should_create = []
        while now_asks and asks:
            if now_asks[0] < asks[0]:
                logger.info(f"Cancel: {now_asks[0]!r}")
                self.cancel_ask(now_asks.pop(0))
            elif now_asks[0] > asks[0]:
                logger.info(f"Create: {asks[0]!r}")
                should_create.append(asks.pop(0))
            else:
                logger.info(f"Equals: {now_asks[0]!r}")
                now_asks.pop(0)
                asks.pop(0)

        for now_ask in now_asks:
            self.cancel_ask(now_ask)

        for ask in should_create:
            self.create_ask(ask)

        for ask in asks:
            self.create_ask(ask)

    @property
    def bids(self):
        """Deprecated: ambiguous name"""
        warn(DeprecationWarning("ambiguous name 'bids', use 'my_bids' instead"))
        return self._user_character.bids

    @property
    def asks(self):
        """Deprecated: ambiguous name"""
        warn(DeprecationWarning("ambiguous name 'asks', use 'my_asks' instead"))
        return self._user_character.asks

    @property
    def my_bids(self):
        self.refreshes('my_bids')
        return self._user_character.bids

    @property
    def my_asks(self):
        self.refreshes('my_asks')
        return self._user_character.asks

    @property
    def amount(self):
        self.refreshes('amount')
        return self._user_character.amount

    @property
    def name(self):
        self.refreshes('ico_or_character')
        return self._character_info.name

    @property
    def is_ico(self):
        self.refreshes('ico_or_character')
        return isinstance(self._character_info, TICO)

    @property
    def is_on_market(self):
        self.refreshes('ico_or_character')
        return isinstance(self._character_info, TCharacter)

    @property
    def ico_id(self):
        self.refreshes('ico')
        return self._character_info.id

    @property
    def ico_begin(self):
        self.refreshes('ico')
        return self._character_info.begin

    @property
    def ico_end(self):
        self.refreshes('ico')
        return self._character_info.end

    @property
    def ico_total(self):
        self.refreshes('ico')
        return self._character_info.total

    @property
    def ico_my_amount(self):
        self.refreshes('my_ico')
        return self._my_ico.amount

    @property
    def ico_users(self):
        self.refreshes('ico')
        return self._character_info.users

    @property
    def global_holding(self):
        self.refreshes('character')
        return self._character_info.total

    @property
    def current_price(self):
        self.refreshes('character')
        return self._character_info.current

    @property
    def last_order(self):
        self.refreshes('character')
        return self._character_info.last_order

    @property
    def last_deal(self):
        self.refreshes('character')
        return self._character_info.last_deal

    @property
    def global_sacrifices(self):
        self.refreshes('character')
        return self._character_info.sacrifices

    @property
    def rate(self):
        self.refreshes('character')
        return self._character_info.rate

    @property
    def price(self):
        self.refreshes('character')
        return self._character_info.price

    @property
    def charts(self):
        self.refreshes('charts')
        return self._charts

    @property
    def all_asks(self):
        self.refreshes('all_asks')
        return self._depth.asks

    @property
    def all_bids(self):
        self.refreshes('all_bids')
        return self._depth.bids

    @property
    def asks_all(self):
        """Deprecated: ambiguous name"""
        warn(DeprecationWarning("ambiguous name 'asks_all', use 'all_asks' instead"))
        self.refreshes('all_asks')
        return self._depth.asks

    @property
    def bids_all(self):
        """Deprecated: ambiguous name"""
        warn(DeprecationWarning("ambiguous name 'bids_all', use 'all_bids' instead"))
        self.refreshes('all_bids')
        return self._depth.bids
