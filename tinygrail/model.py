from functools import lru_cache
from typing import *
from pydantic import BaseModel
from datetime import datetime


class TBid(BaseModel):
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


class TAsk(BaseModel):
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

class TDepth(BaseModel):
    asks: List[TAsk]
    bids: List[TBid]


class RDepth(BaseModel):
    value: TDepth

    @property
    def highest_bid(self) -> Optional[TBid]:
        try:
            return max(self.value.bids, key=lambda bid: bid.Price)
        except ValueError:
            return None


class TCharacter(BaseModel):
    id: int
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

    @property
    def character_id(self) -> int:
        return self.id


class TICO(BaseModel):
    id: int
    character_id: int
    name: str
    begin: datetime
    end: datetime
    total: float  # 总金额
    users: int


class RCharacterList(BaseModel):
    value: List[Union[TCharacter, TICO]]


class RCharacterish(BaseModel):
    value: Union[TCharacter, TICO]


class TUserCharacter(BaseModel):
    bids: List[TBid]
    asks: List[TAsk]
    amount: int  # 持仓

    @property
    def total_holding(self):
        return self.amount + sum(ask.amount for ask in self.asks)


class RUserCharacter(BaseModel):
    value: TUserCharacter


class TBlueleafCharacter(TCharacter):
    state: int  # 持有


class TBlueleafCharaAll(BaseModel):
    total_items: int
    items: List[TBlueleafCharacter]


class RBlueleafCharaAll(BaseModel):
    value: TBlueleafCharaAll


class TChartum(BaseModel):
    time: str
    begin: float
    end: float
    low: float
    high: float
    amount: int
    price: float


class RCharts(BaseModel):
    value: List[TChartum]


class Player:
    identity: str

    def __init__(self, identity):
        self.identity = identity

    @property
    @lru_cache
    def session(self):
        import requests
        session = requests.Session()

        session.cookies = requests.cookies.cookiejar_from_dict({
            '.AspNetCore.Identity.Application': self.identity
        })

        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.7,en-US;q=0.3',
            'Content-Type': 'application/json',
            'Origin': 'https://bgm.tv',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://bgm.tv/rakuen/topiclist',
        }

        return session

    @property
    @lru_cache
    def aio_session(self):
        from aiohttp_requests import requests
        session = requests.Session()

        session.cookies = requests.cookies.cookiejar_from_dict({
            '.AspNetCore.Identity.Application': self.identity
        })

        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.7,en-US;q=0.3',
            'Content-Type': 'application/json',
            'Origin': 'https://bgm.tv',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://bgm.tv/rakuen/topiclist',
        }

        return session


class TAskCharacter(TCharacter):
    state: int  # 卖单量


class LAskCharacter(BaseModel):
    total_items: int
    items: List[TAskCharacter]


class RAllAsks(BaseModel):
    value: LAskCharacter


class THolding(TCharacter):
    state: int  # 持有


class LHolding(BaseModel):
    total_items: int
    items: List[THolding]


class RHolding(BaseModel):
    value: LHolding


class TAuction(BaseModel):
    amount: int
    total: int
    price: float  # 拍卖底价
    auction_users: int
    auction_total: int


class RAuction(BaseModel):
    value: TAuction


class TTemple(BaseModel):
    name: str
    character_id: int
    assets: int
    sacrifices: int
    level: int


class LTemple(BaseModel):
    total_items: int
    items: List[TTemple]


class RAllTemples(BaseModel):
    value: LTemple


class TMyICO(BaseModel):
    amount: float


class RMyICO(BaseModel):
    value: TMyICO
