from datetime import datetime
from typing import *

from pydantic import validator

from ._base import TinygrailModel
from .history import BHistory, UHistory


class TBid(TinygrailModel):
    price: float
    amount: int
    type: int = 0  # 0 表示明买，1 表示暗买
    id: Optional[int]

    def __lt__(self, other):
        if not isinstance(other, TBid):
            return NotImplemented
        return self.price < other.price or (self.price == other.price and self.amount < other.amount)

    def __eq__(self, other):
        if not isinstance(other, TBid):
            return NotImplemented
        return self.price == other.price and self.amount == other.amount


class TAsk(TinygrailModel):
    price: float
    amount: int
    type: int = 0
    # 0 表示明卖，1 表示暗卖
    id: Optional[int]

    def __lt__(self, other):
        if not isinstance(other, TAsk):
            return NotImplemented
        return self.price < other.price or (self.price == other.price and self.amount < other.amount)

    def __eq__(self, other):
        if not isinstance(other, TAsk):
            return NotImplemented
        return self.price == other.price and self.amount == other.amount


class TAskHistory(TinygrailModel):
    amount: int
    price: float
    id: int
    character_id: int
    trade_time: datetime
    type: int  # 2 表示献祭


class TBidHistory(TinygrailModel):
    amount: int
    price: float
    id: int
    character_id: int
    trade_time: datetime
    type: int  # 4 表示拍卖


class TDepth(TinygrailModel):
    asks: List[TAsk]
    bids: List[TBid]

    @property
    def highest_bid(self) -> Optional[TBid]:
        try:
            return max(self.bids, key=lambda bid: bid.Price)
        except ValueError:
            return None


class RDepth(TinygrailModel):
    value: TDepth


class TCharacter(TinygrailModel):
    id: int
    character_id: int
    name: str
    level: int
    price: float
    current: float
    rate: float
    total: int
    last_order: datetime
    last_deal: datetime
    sacrifices: int
    rate: float


class TICO(TinygrailModel):
    id: int
    character_id: int
    name: str
    begin: datetime
    end: datetime
    total: float  # 总金额
    users: int


class RCharacterList(TinygrailModel):
    value: List[Union[TCharacter, TICO]]


class RCharacterish(TinygrailModel):
    value: Union[TCharacter, TICO]


class TUserCharacter(TinygrailModel):
    bids: List[TBid]
    asks: List[TAsk]
    ask_history: List[TAskHistory]
    bid_history: List[TBidHistory]
    amount: int  # 持仓

    @property
    def total_holding(self):
        return self.amount + sum(ask.amount for ask in self.asks)


class RUserCharacter(TinygrailModel):
    value: TUserCharacter


class TCharaUserChara(TinygrailModel):
    id: int
    sacrifices: int  # 已献祭
    state: int  # 持仓


class LCharaUserChara(TinygrailModel):
    total_items: int
    items: List[TCharaUserChara]


class RCharaUserChara(TinygrailModel):
    value: LCharaUserChara


class TBlueleafCharacter(TCharacter):
    state: int  # 持有


class LBlueleafCharacter(TinygrailModel):
    total_items: int
    items: List[TBlueleafCharacter]


class RBlueleafCharacter(TinygrailModel):
    value: LBlueleafCharacter


class TChartum(TinygrailModel):
    time: str
    begin: float
    end: float
    low: float
    high: float
    amount: int
    price: float


class RCharts(TinygrailModel):
    value: List[TChartum]


class TAskCharacter(TCharacter):
    state: int  # 卖单量


class LAskCharacter(TinygrailModel):
    total_items: int
    items: List[TAskCharacter]


class RAllAsks(TinygrailModel):
    value: LAskCharacter


class THolding(TCharacter):
    state: int  # 持有


class LHolding(TinygrailModel):
    total_items: int
    items: List[THolding]


class RHolding(TinygrailModel):
    value: LHolding


class TAuction(TinygrailModel):
    amount: int
    total: int
    price: float  # 拍卖底价
    auction_users: int
    auction_total: int


class RAuction(TinygrailModel):
    value: TAuction


class TTemple(TinygrailModel):
    name: str
    character_id: int
    assets: int
    sacrifices: int
    level: int


class LTemple(TinygrailModel):
    total_items: int
    items: List[TTemple]


class RAllTemples(TinygrailModel):
    value: LTemple


class TMyICO(TinygrailModel):
    amount: float


class RMyICO(TinygrailModel):
    value: TMyICO


class HistoryParser(TinygrailModel):
    history: UHistory


class LHistory(TinygrailModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    items: List[UHistory]


class RHistory(TinygrailModel):
    state: int
    value: LHistory


class TScratchBonus(TinygrailModel):
    id: int
    name: str
    level: int
    cover: str
    amount: int
    rate: float
    current_price: float
    sell_price: float
    sell_amount: int
    finance_price: float


class RScratchBonus(TinygrailModel):
    state: int
    value: Optional[List[TScratchBonus]]
    message: Optional[str]


class RScratchLikeOnce(TinygrailModel):
    state: int
    value: TScratchBonus


class RString(TinygrailModel):
    state: int
    value: str


class RInteger(TinygrailModel):
    state: int
    value: int


class TUserAssets(TinygrailModel):
    id: int
    name: str
    avatar: str
    nickname: str
    balance: float
    assets: float
    type: int
    state: int
    last_index: int
    show_weekly: bool
    show_daily: bool


class RUserAssets(TinygrailModel):
    state: int
    value: TUserAssets


class RErrorMessage(TinygrailModel):
    state: int
    message: str


class TMinimalUserCharacter(TinygrailModel):
    state: int
    amount: int
    bonus: int
    character_id: int
    icon: Optional[str]
    id: int
    price: float
    sacrifices: int
    total: int
    user_id: int


class RMinimalUserCharacter(TinygrailModel):
    state: int
    value: Union[TMinimalUserCharacter, TAuction]


class TCharacterHolder(TinygrailModel):
    name: str
    nickname: str
    balance: int
    last_active_date: datetime
    avatar: str
    id: int


class LCharacterHolder(TinygrailModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    items: List[TCharacterHolder]


class RCharacterHolder(TinygrailModel):
    state: int
    value: LCharacterHolder


class TTopWeek(TinygrailModel):
    price: float
    extra: float
    character_id: int
    character_name: str
    type: int  # auction users
    assets: int  # total auction stock
    sacrifices: int  # total stock in valhalla
    average_extra: float = 1.0

    @property
    def score_1(self):
        return self.type * self.extra

    @property
    def score_2(self):
        if self.average_extra is None:
            raise
        return self.average_extra * self.type + self.extra


class RTopWeek(TinygrailModel):
    state: int
    value: List[TTopWeek]

    # noinspection PyMethodParameters
    # validator returns class method
    @validator('value')
    def inject_average_extra(cls, v: List[TTopWeek]):
        average_extra = sum((val.extra for val in v)) / sum((val.type for val in v))
        for val in v:
            val.average_extra = average_extra
        return v


class TMyAuction(TinygrailModel):
    price: float
    amount: int
    bid: datetime
    character_id: int
    type: int  # all auction stocks


class RLMyAuction(TinygrailModel):
    state: int
    value: List[TMyAuction]
