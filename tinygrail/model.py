import re
from datetime import datetime
from functools import lru_cache
from typing import *

from inflection import camelize
from pydantic import BaseModel, validator

from .helper import *


class TinygrailModel(BaseModel):
    class Config:
        alias_generator = camelize


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


class TBlueleafCharaAll(TinygrailModel):
    total_items: int
    items: List[TBlueleafCharacter]


class RBlueleafCharaAll(TinygrailModel):
    value: TBlueleafCharaAll


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


class Player:
    identity: str

    def __init__(self, identity):
        self.identity = identity

    @property
    @lru_cache
    def session(self):
        import requests
        session = requests.Session()

        session.cookies['.AspNetCore.Identity.Application'] = self.identity

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

        session.cookies['.AspNetCore.Identity.Application'] = self.identity

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


class BHistory(TinygrailModel):
    description: str
    parsed_description: Optional[re.Match] = None
    related_name: Optional[str]
    id: int  # history id
    user_id: int
    related_id: int
    change: float
    amount: int
    balance: float
    log_time: datetime
    type: int
    state: int
    DESCRIPTION_PARSER: ClassVar[re.Pattern] = None

    class Config:
        arbitrary_types_allowed = True
        alias_generator = camelize

    # noinspection PyMethodParameters
    # validator returns class method
    @validator('parsed_description', always=True)
    def parse_description(cls, v, values, **kwargs):
        if v is not None:
            return v
        if cls.DESCRIPTION_PARSER is None:
            return None
        parsed_description = cls.DESCRIPTION_PARSER.fullmatch(values['description'])
        if parsed_description is None:
            raise ValueError("unable to parse description")
        return parsed_description


class THistoryBangumiDays(BHistory):
    type: Literal[1]
    related_id: Literal[1]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"bangumi注册(\d+)天奖励")
    days: int = None
    _parse_stocks = parsed_group('days', 1)


class THistoryDaily(BHistory):
    type: Literal[1]
    related_id: Literal[2]
    description: Literal['bangumi每日登录奖励']


class THistoryCellPhone(BHistory):
    type: Literal[1]
    related_id: Literal[3]
    description: Literal['绑定手机奖励']


class THistoryShareBonus(BHistory):
    type: Literal[1]
    related_id: Literal[6]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"每周基础股息分红，共计(\d+)股。")
    stocks: int = None
    _parse_stocks = parsed_group('stocks', 1)


class THistoryHappyNewYear(BHistory):
    type: Literal[1]
    related_id: Literal[7]
    description: Literal['新年福利']


class THistoryScratchBonusPay(BHistory):
    type: Literal[1]
    related_id: Literal[8]
    description: Literal['购买刮刮乐彩票']


class THistoryScratchBonusResult(BHistory):
    type: Literal[1]
    related_id: Literal[8, 10]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"彩票刮刮乐获奖 #(\d+)「(.+)」(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _amounts_match = parsed_match('amount', 3, translate=int)


class THistoryGensokyoPay(BHistory):
    type: Literal[1]
    related_id: Literal[8, 10]
    description: Literal['购买幻想乡彩票']


class THistoryGensokyoResult(BHistory):
    type: Literal[1]
    related_id: Literal[8, 10]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"幻想乡彩票获奖 #(\d+)「(.+)」(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _amounts_match = parsed_match('amount', 3, translate=int)


class THistoryInvited(BHistory):
    type: Literal[1]
    description: Literal['被推荐奖励']


class THistoryEnterICO(BHistory):
    type: Literal[2]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"参与ICO #(\d+)「(.+)」")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryStartICO(BHistory):
    type: Literal[2]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"发起ICO #(\d+)「(.+)」")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryICORest(BHistory):
    type: Literal[3]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"ICO成功退回余额 #(\d+)「(.+)」")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryICOFail(BHistory):
    type: Literal[3]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"ICO失败退款 #(\d+)「(.+)」")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryBid(BHistory):
    type: Literal[4]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"买入委托 #(\d+)「(.+)」冻结([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryBidDeal(BHistory):
    type: Literal[4]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"(?:买入成交|买入委托)\((\d+)\) #(\d+)「(.+)」(?:买进|成交)(\d+)股")
    bid_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_bid_id = parsed_group('bid_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)
    _amounts_match = parsed_match('amount', 4, translate=int)


class THistoryBidDealRest(BHistory):
    type: Literal[4]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"(?:买入成交|买入委托|买入委托完成) #(\d+)「(.+)」余额解除冻结([\d.Ee+-]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryIcebergBid(BHistory):
    type: Literal[4]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"冰山买入委托 #(\d+)「(.+)」冻结([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryIcebergBidDeal(BHistory):
    type: Literal[4]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"冰山买入委托\((\d+)\) #(\d+)「(.+)」成交(\d+)股")
    bid_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_bid_id = parsed_group('bid_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)
    _amounts_match = parsed_match('amount', 4, translate=int)


class THistoryCancelBid(BHistory):
    type: Literal[5]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"取消买入委托\((\d+)\) #(\d+)「(.+)」解除冻结([\d.]+)cc")
    bid_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_bid_id = parsed_group('bid_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)


class THistoryAsk(BHistory):
    type: Literal[6]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"卖出委托 #(\d+)「(.+)」冻结(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amounts_match = parsed_match('amount', 3, translate=lambda x: -int(x))


class THistoryIceBergAsk(BHistory):
    type: Literal[6]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"冰山卖出委托 #(\d+)「(.+)」冻结(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amounts_match = parsed_match('amount', 3, translate=lambda x: -int(x))


class THistoryAskDeal(BHistory):
    type: Literal[6]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"(?:卖出委托|卖出成交)\((\d+)\) #(\d+)「(.+)」售出(\d+)股\((?:ask|bid)\)")
    ask_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_ask_id = parsed_group('ask_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)
    _amounts_match = parsed_match('amount', 4, translate=lambda x: -int(x))


class THistoryIceBergAskDeal(BHistory):
    type: Literal[6]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(
        r"冰山卖出委托\((\d+)\) #(\d+)「(.+)」售出(\d+)股\(ask\)")
    ask_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_ask_id = parsed_group('ask_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)
    _amounts_match = parsed_match('amount', 4, translate=lambda x: -int(x))


class THistoryChangeAuctionServiceCharge(BHistory):
    type: Literal[7]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"修改竞拍 #(\d+)「(.+)」收取手续费([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryCancelAuctionServiceCharge(BHistory):
    type: Literal[7]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"取消竞拍 #(\d+)「(.+)」收取手续费([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryDealServiceCharge(BHistory):
    type: Literal[7]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"交易印花税 #(\d+)「(.+)」")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryCancelAsk(BHistory):
    type: Literal[8]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"取消卖出委托\((\d+)\) #(\d+)「(.+)」解除冻结(\d+)股")
    ask_id: int = None
    character_id: int = None
    character_name: str = None
    _parse_bid_id = parsed_group('ask_id', 1)
    _parse_character_id = parsed_group('character_id', 2)
    _parse_character_name = parsed_group('character_name', 3)
    _cid_match = parsed_match('related_id', 2, translate=int)
    _amounts_match = parsed_match('amount', 4, translate=int)


class THistorySacrifice(BHistory):
    type: Literal[9]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"资产重组 #(\d+)「(.+)」共(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amount_match = parsed_match('amount', 3, translate=int)


class THistoryCapital(BHistory):
    type: Literal[9]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"股权融资 #(\d+)「(.+)」共(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amount_match = parsed_match('amount', 3, translate=int)


class THistoryChangeAuctionEnter(BHistory):
    type: Literal[10]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"参与竞拍 #(\d+)「(.+)」冻结([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryChangeAuctionChangeFreeze(BHistory):
    type: Literal[10]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"修改竞拍 #(\d+)「(.+)」冻结-([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryChangeAuctionChangeUnfreeze(BHistory):
    type: Literal[11]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"修改竞拍 #(\d+)「(.+)」解除冻结([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)


class THistoryChangeAuctionCancelUnfreeze(BHistory):
    type: Literal[11]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"取消竞拍 #(\d+)「(.+)」解除冻结([\d.]+)cc")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryAuctionSuccess(BHistory):
    type: Literal[12]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"竞拍 #(\d+)「(.+)」成功获得(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _amount_match = parsed_match('amount', 3, translate=int)


class THistoryAuctionFail(BHistory):
    type: Literal[12]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"竞拍 #(\d+)「(.+)」失败解除冻结")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryAuctionTop3(BHistory):
    type: Literal[12]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"为萌王 #(\d+)「(.+)」的诞生献上祝福")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)


class THistoryICOResult(BHistory):
    type: Literal[13]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"ICO成功获得 #(\d+)「(.+)」共(\d+)股")
    character_id: int = None
    character_name: str = None
    stocks: int = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _parse_stocks = parsed_match('stocks', 3)


class THistoryTax(BHistory):
    type: Literal[14]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"个人所得税 ₵([\d.]+) / ([\d.]+)")
    tax_amount: float = None
    taxed_target: float = None
    _parse_tax_amount = parsed_group('tax_amount', 1)
    _parse_taxed_target = parsed_group('taxed_target', 2)


class THistorySend(BHistory):
    type: Literal[16]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"给「(.+)」发送红包")
    target_name: str = None
    _parse_target_name = parsed_group('target_name', 1)

    @property
    def target_id(self):
        return self.related_id


class THistoryReceive(BHistory):
    type: Literal[17]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"收到来自「(.+)」的红包")
    from_name: str = None
    _parse_target_name = parsed_group('from_name', 1)

    @property
    def target_id(self):
        return self.related_id


class THistoryChaos(BHistory):
    type: Literal[18]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"使用「混沌魔方」获得 ?#(\d+)「(.+)」(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amount_match = parsed_match('amount', 3, translate=int)


class THistoryChaosDamage(BHistory):
    type: Literal[18]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"受到「混沌魔方」攻击损失 #(\d+)「(.+)」(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amount_match = parsed_match('amount', 3, translate=lambda x: -int(x))


class THistoryGuidepost(BHistory):
    type: Literal[18]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"使用「虚空道标」获得 #(\d+)「(.+)」(\d+)股")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _amount_match = parsed_match('amount', 3, translate=int)


class THistoryGuidepostDamage(BHistory):
    type: Literal[18]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"受到「虚空道标」攻击损失 #(\d+)「(.+)」(\d+)股固定资产")
    character_id: int = None
    character_name: str = None
    _parse_character_id = parsed_group('character_id', 1)
    _parse_character_name = parsed_group('character_name', 2)
    _amount_match = parsed_match('amount', 3, translate=lambda x: -int(x))


class THistoryStardust(BHistory):
    type: Literal[18]

    DESCRIPTION_PARSER: ClassVar[re.Pattern] = re.compile(r"使用 #(\d+)「\$(.+)」通过「星光碎片」为 #(\d+)「\$(.+)」充能(\d+)股")
    supplier_character_id: int = None
    supplier_character_name: str = None
    demand_character_id: int = None
    demand_character_name: str = None
    _parse_supplier_character_id = parsed_group('supplier_character_id', 1)
    _parse_supplier_character_name = parsed_group('supplier_character_name', 2)
    _parse_demand_character_id = parsed_group('demand_character_id', 3)
    _parse_demand_character_name = parsed_group('demand_character_name', 4)
    _cid_match = parsed_match('related_id', 1, translate=int)
    _amount_match = parsed_match('amount', 5, translate=int)


class HistoryParser(TinygrailModel):
    history: Union[(*BHistory.__subclasses__(),)]


class LHistory(TinygrailModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    items: List[Union[(*BHistory.__subclasses__(),)]]


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
