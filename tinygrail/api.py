import itertools
import logging

from pydantic import ValidationError

import requests_as_model
from .model import *

requests_as_model.monkey_patch()

logger = logging.getLogger('tinygrail.api')

REQUEST_TIMEOUT = 10


def batch_character_info(player, lst, splits=50) -> List[Union[TCharacter, TICO]]:
    lst = list(lst)
    ans = []
    while lst:
        head50 = lst[:splits]
        lst = lst[splits:]
        response = player.session.post('https://tinygrail.com/api/chara/list', json=head50, timeout=REQUEST_TIMEOUT)
        obj = response.as_model(RCharacterList)
        ans.extend(obj.value)
    return ans


def character_info(player, cid) -> RCharacterish:
    response = player.session.get(f"https://tinygrail.com/api/chara/{cid}", timeout=REQUEST_TIMEOUT)
    return response.as_model(RCharacterish)


def depth(player, cid) -> TDepth:
    response = player.session.get(f"https://tinygrail.com/api/chara/depth/{cid}", timeout=REQUEST_TIMEOUT)
    obj = response.as_model(RDepth)
    return obj.value


def user_character(player, cid) -> RUserCharacter:
    response = player.session.get(f"https://tinygrail.com/api/chara/user/{cid}", timeout=REQUEST_TIMEOUT)
    obj = response.as_model(RUserCharacter)
    return obj


def chara_user_character(player) -> List[TCharaUserChara]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RCharaUserChara).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/1/{length}",
                               timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RCharaUserChara).value.items
    return lst


def blueleaf_chara_all(player) -> RBlueleafCharaAll:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RBlueleafCharaAll).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/{length}",
                               timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RBlueleafCharaAll)
    return lst


def chara_charts(player, cid) -> List[TChartum]:
    response = player.session.get(f"https://tinygrail.com/api/chara/charts/{cid}/2019-08-08", timeout=REQUEST_TIMEOUT)
    obj = response.as_model(RCharts)
    return obj.value


def all_asks(player: Player) -> List[TCharacter]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RAllAsks).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/{length}", timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RAllAsks).value.items
    return lst


def all_bids(player: Player) -> List[TCharacter]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/bids/0/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RAllAsks).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/bids/0/1/{length}", timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RAllAsks).value.items
    return lst


def all_holding(player: Player) -> List[THolding]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/0/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RHolding).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/0/1/{length}", timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RHolding).value.items
    return lst


def create_bid(player: Player, cid: int, bid: TBid):
    url = f"https://tinygrail.com/api/chara/bid/{cid}/{bid.price}/{bid.amount}"
    if bid.type == 1:
        url += "/true"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    result = response.as_model(RString)
    return result


def create_ask(player: Player, cid: int, ask: TAsk):
    url = f"https://tinygrail.com/api/chara/ask/{cid}/{ask.price}/{ask.amount}"
    if ask.type == 1:
        url += "/true"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    result = response.as_model(RString)
    return result


def cancel_bid(player: Player, bid: TBid):
    assert bid.id is not None, ValueError
    url = f"https://tinygrail.com/api/chara/bid/cancel/{bid.id}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    result = response.as_model(RString)
    return result


def cancel_ask(player: Player, ask: TAsk):
    assert ask.id is not None, ValueError
    url = f"https://tinygrail.com/api/chara/ask/cancel/{ask.id}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    result = response.as_model(RString)
    return result


def get_initial_price(player: Player, cid: int):
    cc = chara_charts(player, cid)
    return cc[0].begin


def character_auction(player: Player, cid: int) -> TAuction:
    url = f"https://tinygrail.com/api/chara/user/{cid}/tinygrail/false"
    response = player.session.get(url, timeout=REQUEST_TIMEOUT)
    return response.as_model(RAuction).value


def user_temples(player: Player) -> List[TTemple]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/temple/0/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RAllTemples).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/temple/0/1/{length}", timeout=REQUEST_TIMEOUT)
    lst = resp2.as_model(RAllTemples).value.items
    return lst


def magic_chaos(player: Player, attacker_cid: int) -> TScratchBonus:
    url = f"https://tinygrail.com/api/magic/chaos/{attacker_cid}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    jso = response.as_model(RScratchLikeOnce).value
    return jso


def magic_guidepost(player: Player, attacker_cid: int, target_cid: int) -> TScratchBonus:
    url = f"https://tinygrail.com/api/magic/guidepost/{attacker_cid}/{target_cid}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    jso = response.as_model(RScratchLikeOnce).value
    return jso


def magic_stardust(player: Player, supplier_cid: int, demand_cid: int, amount: int,
                   use_type: Literal['position', 'temple']):
    if use_type == 'position':
        is_temple = 'false'
    elif use_type == 'temple':
        is_temple = 'true'
    else:
        raise ValueError(f"You can only use 'position' or 'temple', not {use_type!r}")
    url = f"https://tinygrail.com/api/magic/stardust/{supplier_cid}/{demand_cid}/{amount}/{is_temple}"
    response = player.session.post(url, json=None, timeout=REQUEST_TIMEOUT)
    jso = response.json()
    return jso


def get_my_ico(player: Player, ico_id: int) -> TMyICO:
    response = player.session.get(f"https://tinygrail.com/api/chara/initial/{ico_id}", timeout=REQUEST_TIMEOUT)
    return response.as_model(RMyICO).value


def get_history(player: Player) -> List[BHistory]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/balance/1/1", timeout=REQUEST_TIMEOUT)
    length = response.as_model(RHistory).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/balance/1/{length}", timeout=REQUEST_TIMEOUT)
    try:
        lst = resp2.as_model(RHistory).value.items
    except requests_as_model.APIResponseSchemeNotMatch:
        raw_histories = resp2.json()['Value']['Items']
        for raw_history in raw_histories:
            assert isinstance(raw_history, dict)
            try:
                assert isinstance(HistoryParser(History=raw_history).history, BHistory)
            except ValidationError:
                raise requests_as_model.APIResponseSchemeNotMatch(resp2, raw_history) from None
        raise
    return lst


def get_history_since_id(player: Player, since_id: int = 0, page_limit: int = None) -> List[BHistory]:
    # get list length
    fetched: Dict[int, BHistory] = {}
    page_id_iterator = (itertools.count(1) if page_limit is None else range(1, page_limit + 1))
    for page in page_id_iterator:
        response = player.session.get(f"https://tinygrail.com/api/chara/user/balance/{page}/50",
                                      timeout=REQUEST_TIMEOUT)
        try:
            lst: List[BHistory] = response.as_model(RHistory).value.items
        except requests_as_model.APIResponseSchemeNotMatch:
            lst = []
            raw_histories = response.json()['Value']['Items']
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


def scratch_bonus2(player: Player) -> List[TScratchBonus]:
    response = player.session.get("https://tinygrail.com/api/event/scratch/bonus2", timeout=REQUEST_TIMEOUT)
    return response.as_model(RScratchBonus).value


def scratch_gensokyo(player: Player) -> List[TScratchBonus]:
    response = player.session.get("https://tinygrail.com/api/event/scratch/bonus2/true", timeout=REQUEST_TIMEOUT)
    return response.as_model(RScratchBonus).value


def scratch_gensokyo_price(player: Player) -> int:
    response = player.session.get("https://tinygrail.com/api/event/daily/count/10", timeout=REQUEST_TIMEOUT)
    return 2000 * (2 ** response.as_model(RInteger).value)
