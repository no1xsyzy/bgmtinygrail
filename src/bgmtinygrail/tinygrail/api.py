import itertools
import logging

from pydantic import ValidationError

from .model import *
from .player import Player, APIResponseSchemeNotMatch, dummy_player

logger = logging.getLogger('tinygrail.api')

REQUEST_TIMEOUT = 10


def batch_character_info(player: Player, lst: List[int], splits=1000) -> List[Union[TCharacter, TICO]]:
    lst = [int(c) for c in lst]
    ans = []
    while lst:
        head50 = lst[:splits]
        lst = lst[splits:]
        obj = player.post_data('chara/list', head50, as_model=RCharacterList)
        ans.extend(obj.value)
    return ans


def character_info(player: Player, cid: int) -> Union[TCharacter, TICO]:
    return player.get_data(f"chara/{cid}", as_model=RCharacterish).value


def depth(player: Player, cid: int) -> TDepth:
    return player.get_data(f"chara/depth/{cid}", as_model=RDepth).value


def user_character(player: Player, cid: int) -> TUserCharacter:
    return player.get_data(f"chara/user/{cid}", as_model=RUserCharacter).value


def blueleaf_chara_all(player: Player) -> List[TBlueleafCharacter]:
    length = player.get_data("chara/user/chara/blueleaf/1/1",
                             RBlueleafCharacter).value.total_items
    if length == 0:
        return []
    lst = player.get_data(f"chara/user/chara/blueleaf/1/{length}",
                          RBlueleafCharacter).value.items
    return lst


def chara_charts(player: Player, cid: int) -> List[TChartum]:
    return player.get_data(f"chara/charts/{cid}/2019-08-08", as_model=RCharts).value


def all_asks(player: Player) -> List[TCharacter]:
    length = player.get_data("chara/asks/0/1/1", as_model=RAllAsks).value.total_items
    if length == 0:
        return []
    return player.get_data(f"chara/asks/0/1/{length}", as_model=RAllAsks).value.items


def all_bids(player: Player) -> List[TCharacter]:
    length = player.get_data("chara/bids/0/1/1", as_model=RAllAsks).value.total_items
    if length == 0:
        return []
    return player.get_data(f"chara/bids/0/1/{length}", as_model=RAllAsks).value.items


def iter_holding(player: Player, page_size: int = 50) -> List[TCharaUserChara]:
    for page in itertools.count(1):
        holdings = player.get_data(f"chara/user/chara/0/{page}/{page_size}",
                                   as_model=RCharaUserChara).value.items
        if holdings:
            yield from holdings
        else:
            break


def all_holding(player: Player) -> List[THolding]:
    length = player.get_data("chara/user/chara/0/1/1", as_model=RHolding).value.total_items
    if length == 0:
        return []
    return player.get_data(f"chara/user/chara/0/1/{length}", as_model=RHolding).value.items


def get_full_holding(player: Player) -> Dict[int, Tuple[int, int]]:
    characters = {}
    for c in all_holding(player):
        characters[c.id] = (c.state, c.sacrifices)
    for c in user_temples(player):
        if c.character_id not in characters:
            characters[c.character_id] = 0, c.sacrifices
    return characters


def get_full_holding_2(player: Player) -> Dict[int, Union[TTemple, THolding]]:
    characters = {}
    for c in all_holding(player):
        characters[c.character_id] = c
    for c in user_temples(player):
        if c.character_id not in characters:
            characters[c.character_id] = c
    return characters


def create_bid(player: Player, cid: int, bid: TBid):
    url = f"chara/bid/{cid}/{bid.price}/{bid.amount}"
    if bid.type == 1:
        url += "/true"
    return player.post_data(url, data=None, as_model=RString)


def create_ask(player: Player, cid: int, ask: TAsk):
    url = f"chara/ask/{cid}/{ask.price}/{ask.amount}"
    if ask.type == 1:
        url += "/true"
    return player.post_data(url, data=None, as_model=RString)


def cancel_bid(player: Player, bid: TBid):
    assert bid.id is not None, ValueError
    url = f"chara/bid/cancel/{bid.id}"
    return player.post_data(url, data=None, as_model=RString)


def cancel_ask(player: Player, ask: TAsk):
    assert ask.id is not None, ValueError
    url = f"chara/ask/cancel/{ask.id}"
    return player.post_data(url, data=None, as_model=RString)


def get_initial_price(player: Player, cid: int):
    cc = chara_charts(player, cid)
    return cc[0].begin


def character_auction(player: Player, cid: int) -> TAuction:
    url = f"chara/user/{cid}/tinygrail/false"
    return player.get_data(url, as_model=RAuction).value


def user_temples(player: Player) -> List[TTemple]:
    length = player.get_data("chara/user/temple/0/1/1",
                             as_model=RAllTemples).value.total_items
    if length == 0:
        return []
    return player.get_data(f"chara/user/temple/0/1/{length}",
                           as_model=RAllTemples).value.items


def magic_chaos(player: Player, attacker_cid: int) -> TScratchBonus:
    url = f"magic/chaos/{attacker_cid}"
    return player.post_data(url, data=None, as_model=RScratchLikeOnce).value


def magic_guidepost(player: Player, attacker_cid: int, target_cid: int) -> TScratchBonus:
    url = f"magic/guidepost/{attacker_cid}/{target_cid}"
    return player.post_data(url, data=None, as_model=RScratchLikeOnce).value


def magic_stardust(player: Player, supplier_cid: int, demand_cid: int, amount: int,
                   use_type: Literal['position', 'temple']):
    if use_type == 'position':
        is_temple = 'false'
    elif use_type == 'temple':
        is_temple = 'true'
    else:
        raise ValueError(f"You can only use 'position' or 'temple', not {use_type!r}")
    url = f"magic/stardust/{supplier_cid}/{demand_cid}/{amount}/{is_temple}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    jso = response.json()
    return jso


def get_my_ico(player: Player, ico_id: int) -> TMyICO:
    return player.get_data(f"chara/initial/{ico_id}", as_model=RMyICO).value


def get_history(player: Player, *, since_id: int = 0, page_limit: int = None, page_size: int = 50) -> List[BHistory]:
    fetched: Dict[int, BHistory] = {}
    page_id_iterator = (itertools.count(1) if page_limit is None else range(1, page_limit + 1))
    for page in page_id_iterator:
        jso = player.get_data(f"chara/user/balance/{page}/{page_size}", as_model=None)
        try:
            lst: List[BHistory] = RHistory(**jso).value.items
        except APIResponseSchemeNotMatch:
            lst = []
            raw_histories = jso['Value']['Items']
            for raw_history in raw_histories:
                try:
                    lst.append(HistoryParser(History=raw_history).history)
                except ValidationError:
                    logger.error(f"Bad history: {raw_history}")
        for history in lst:
            if history.id > since_id:
                fetched[history.id] = history
            else:
                break  # for history in lst
        if not lst or lst[-1].id <= since_id:
            break  # for page in page_id_iterator
    return [fetched[cid] for cid in sorted(fetched.keys(), reverse=True)]


def iter_history(player: Player, *, page_size: int = 50) -> Iterator[BHistory]:
    for page in itertools.count(1):
        jso = player.get_data(f"chara/user/balance/{page}/{page_size}", as_model=None)
        try:
            lst: List[BHistory] = RHistory(**jso).value.items
        except APIResponseSchemeNotMatch:
            raw_histories = jso['Value']['Items']
            for raw_history in raw_histories:
                try:
                    yield HistoryParser(History=raw_history).history
                except ValidationError:
                    logger.error(f"Bad history: {raw_history}")
        else:
            if not lst:
                break
            for history in lst:
                yield history


def scratch_bonus2(player: Player) -> List[TScratchBonus]:
    return player.get_data("event/scratch/bonus2", as_model=RScratchBonus).value


def scratch_gensokyo(player: Player) -> List[TScratchBonus]:
    return player.get_data("event/scratch/bonus2/true", as_model=RScratchBonus).value


def scratch_gensokyo_price(player: Player) -> int:
    sp = player.get_data("event/daily/count/10", as_model=RInteger).value
    return 2000 * (2 ** sp)


def user_assets(player: Player) -> TUserAssets:
    return player.get_data("chara/user/assets", as_model=RUserAssets).value


def minimal_user_character(player: Player, cid: int, user_name: Optional[Union[int, str]]) -> TMinimalUserCharacter:
    if user_name is None:
        user_name = 0
    url = f"chara/user/{cid}/{user_name}/false"
    return player.get_data(url, as_model=RMinimalUserCharacter).value


def all_holders(player: Player, cid: int) -> List[TCharacterHolder]:
    length = player.get_data(f"chara/users/{cid}/1/1",
                             as_model=RCharacterHolder).value.total_items
    if length == 0:
        return []
    return player.get_data(f"chara/users/{cid}/1/{length}",
                           as_model=RCharacterHolder).value.items


def spoil_holders(player: Player, cid: int) -> List[Tuple[TMinimalUserCharacter, TCharacterHolder]]:
    holders = all_holders(player, cid)
    result: List[Tuple[TMinimalUserCharacter, TCharacterHolder]] = []
    for holder in holders:
        result.append((minimal_user_character(player, cid, holder.name), holder))
    return result


def top_week() -> List[TTopWeek]:
    return dummy_player.get_data(f"chara/topweek",
                                 as_model=RTopWeek).value


def my_auctions(player: Player, character_ids: List[int]) -> List[TMyAuction]:
    return player.post_data("chara/auction/list", data=character_ids,
                            as_model=RLMyAuction).value


def do_auction(player: Player, cid: int, price: float, amount: int):
    return player.post_data(f"chara/auction/{cid}/{price}/{amount}", data=None,
                            as_model=RString).value


def get_weekly_share(player: Player) -> str:
    return player.get_data(f"event/share/bonus", as_model=RString).value


def get_daily_bonus(player: Player) -> str:
    return player.get_data(f"event/bangumi/bonus/daily", as_model=RString).value


def iter_most_recent_initials(*, page_size: int = 50) -> Iterator[TICO]:
    for page in itertools.count(1):
        initials = dummy_player.get_data(f"chara/mri/{page}/{page_size}", as_model=RMultiICO).value
        if initials:
            yield from initials


def iter_most_valuable_initials(*, page_size: int = 50) -> Iterator[TICO]:
    for page in itertools.count(1):
        initials = dummy_player.get_data(f"chara/mvi/{page}/{page_size}", as_model=RMultiICO).value
        if initials:
            yield from initials


def iter_recent_active_initials(*, page_size: int = 50) -> Iterator[TICO]:
    for page in itertools.count(1):
        initials = dummy_player.get_data(f"chara/rai/{page}/{page_size}", as_model=RMultiICO).value
        if initials:
            yield from initials


def iter_my_initials(player: Player, *, page_size: int) -> Iterator[TICO]:
    for page in itertools.count(1):
        initials = player.get_data(f"chara/user/initial/0/{page}/{page_size}", as_model=RLICO).value.items
        if initials:
            yield from initials
