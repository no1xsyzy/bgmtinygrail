from dataclasses import dataclass
from typing import *
from functools import lru_cache
import requests


@dataclass
class TBid:
    price: float
    amount: int


@dataclass
class TAsk:
    price: float
    amount: int
    id: int


@dataclass
class TDepth:
    asks: List[TAsk]
    bids: List[TBid]


@dataclass
class RDepth:
    value: TDepth

    @property
    def highest_bid(self) -> Optional[TBid]:
        try:
            return max(self.value.bids, key=lambda bid: bid.Price)
        except ValueError:
            return None


@dataclass
class TCharacter:
    id: int
    name: str
    level: int

    @property
    def character_id(self) -> int:
        return self.id


@dataclass
class TICO:
    id: int
    character_id: int
    name: str


@dataclass
class RCharacterList:
    value: List[Union[TCharacter, TICO]]


@dataclass
class RCharacterish:
    value: Union[TCharacter, TICO]


@dataclass
class TUserCharacter:
    bids: List[TBid]
    asks: List[TAsk]


@dataclass
class RUserCharacter:
    value: TUserCharacter


@dataclass
class TBlueleafCharacter(TCharacter):
    state: int  # 持有


@dataclass
class TBlueleafCharaAll:
    total_pages: int
    total_items: int
    items: List[TBlueleafCharacter]


@dataclass
class RBlueleafCharaAll:
    value: TBlueleafCharaAll


@dataclass
class TChartum:
    time: str
    begin: float
    end: float
    low: float
    high: float
    amount: int
    price: float


@dataclass
class RCharts:
    Value: List[TChartum]


@dataclass(frozen=True)
class Player:
    identity: str

    @property
    @lru_cache
    def session(self):
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


@dataclass
class TAskCharacter(TCharacter):
    state: int  # 卖单量


@dataclass
class LAskCharacter:
    total_items: int
    items: List[TAskCharacter]


@dataclass
class RAllAsks:
    value: LAskCharacter
