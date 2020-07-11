import json
import logging

from .model import *

logger = logging.getLogger('tinygrail.api')


def batch_character_info(player, lst, splits=50) -> List[Union[TCharacter, TICO]]:
    lst = list(lst)
    ans = []
    while lst:
        head50 = lst[:splits]
        lst = lst[splits:]
        data = json.dumps(head50)
        response = player.session.post('https://tinygrail.com/api/chara/list', data=data)
        jso = snaky(response.json())
        obj = RCharacterList(**jso)
        ans.extend(obj.value)
    return ans


def character_info(player, cid) -> RCharacterish:
    response = player.session.get(f"https://tinygrail.com/api/chara/{cid}")
    jso = snaky(response.json())
    obj = RCharacterish(**jso)
    return obj


def depth(player, cid) -> TDepth:
    response = player.session.get(f"https://tinygrail.com/api/chara/depth/{cid}")
    jso = snaky(response.json())
    obj = RDepth(**jso)
    return obj.value


def user_character(player, cid) -> RUserCharacter:
    response = player.session.get(f"https://tinygrail.com/api/chara/user/{cid}")
    jso = snaky(response.json())
    obj = RUserCharacter(**jso)
    return obj


def blueleaf_chara_all(player) -> RBlueleafCharaAll:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/1")
    jso = snaky(response.json())
    length = RBlueleafCharaAll(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RBlueleafCharaAll(**jso2)
    return lst


def chara_charts(player, cid) -> List[TChartum]:
    response = player.session.get(f"https://tinygrail.com/api/chara/charts/{cid}/2019-08-08")
    jso = snaky(response.json())
    obj = RCharts(**jso)
    return obj.value


def all_asks(player: Player) -> List[TCharacter]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/1")
    jso = snaky(response.json())
    length = RAllAsks(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RAllAsks(**jso2).value.items
    return lst


def all_bids(player: Player) -> List[TCharacter]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/bids/0/1/1")
    jso = snaky(response.json())
    length = RAllAsks(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/bids/0/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RAllAsks(**jso2).value.items
    return lst


def all_holding(player: Player) -> List[THolding]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/0/1/1")
    jso = snaky(response.json())
    logger.debug(jso)
    length = RHolding(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/0/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RHolding(**jso2).value.items
    return lst


def create_bid(player: Player, cid: int, bid: TBid):
    url = f"https://tinygrail.com/api/chara/bid/{cid}/{bid.price}/{bid.amount}"
    if bid.type == 1:
        url += "/true"
    response = player.session.post(url, data="null")
    jso = response.json()
    logger.debug(jso)
    return jso


def create_ask(player: Player, cid: int, ask: TAsk):
    url = f"https://tinygrail.com/api/chara/ask/{cid}/{ask.price}/{ask.amount}"
    if ask.type == 1:
        url += "/true"
    response = player.session.post(url, data="null")
    jso = response.json()
    logger.debug(jso)
    return jso


def cancel_bid(player: Player, bid: TBid):
    assert bid.id is not None, ValueError
    url = f"https://tinygrail.com/api/chara/bid/cancel/{bid.id}"
    response = player.session.post(url, data="null")
    jso = response.json()
    logger.debug(jso)
    return jso


def cancel_ask(player: Player, ask: TAsk):
    assert ask.id is not None, ValueError
    url = f"https://tinygrail.com/api/chara/ask/cancel/{ask.id}"
    response = player.session.post(url, data="null")
    jso = response.json()
    logger.debug(jso)
    return jso


def get_initial_price(player: Player, cid: int):
    cc = chara_charts(player, cid)
    return cc[0].begin


def character_auction(player: Player, cid: int) -> TAuction:
    url = f"https://tinygrail.com/api/chara/user/{cid}/tinygrail/false"
    response = player.session.get(url)
    jso = snaky(response.json())
    return RAuction(**jso).value


def user_temples(player: Player) -> List[TTemple]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/temple/0/1/1")
    jso = snaky(response.json())
    length = RAllTemples(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/temple/0/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RAllTemples(**jso2).value.items
    return lst


def magic_chaos(player: Player, attacker_cid: int):
    url = f"https://tinygrail.com/api/magic/chaos/{attacker_cid}"
    response = player.session.post(url, json=None)
    jso = snaky(response.json())
    return jso


def magic_guidepost(player: Player, attacker_cid: int, target_cid: int):
    url = f"https://tinygrail.com/api/magic/guidepost/{attacker_cid}/{target_cid}"
    response = player.session.post(url, json=None)
    jso = snaky(response.json())
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
    response = player.session.post(url, json=None)
    jso = snaky(response.json())
    return jso


def get_my_ico(player: Player, ico_id: int) -> TMyICO:
    response = player.session.get(f"https://tinygrail.com/api/chara/initial/{ico_id}")
    jso = snaky(response.json())
    return RMyICO(**jso).value


def get_history(player: Player) -> List[BHistory]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/balance/1/1")
    jso = snaky(response.json())
    length = RHistory(**jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/balance/1/{length}")
    jso2 = snaky(resp2.json())
    lst = RHistory(**jso2).value.items
    return lst
