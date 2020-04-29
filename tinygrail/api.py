import json
from dacite import from_dict
from .model import *
from .helper import *


def batch_character_info(player, lst, splits=50) -> List[Union[TCharacter, TICO]]:
    lst = list(lst)
    ans = []
    while lst:
        head50 = lst[:splits]
        lst = lst[splits:]
        data = json.dumps(head50)
        response = player.session.post('https://tinygrail.com/api/chara/list', data=data)
        jso = snaky(response.json())
        obj = from_dict(RCharacterList, jso)
        ans.extend(obj.value)
    return ans


def character_info(player, cid) -> RCharacterish:
    response = player.session.get(f"https://tinygrail.com/api/chara/{cid}")
    jso = snaky(response.json())
    obj = from_dict(RCharacterish, jso)
    return obj


def depth(player, cid) -> RDepth:
    response = player.session.get(f"https://tinygrail.com/api/chara/depth/{cid}")
    jso = snaky(response.json())
    obj = from_dict(RDepth, jso)
    return obj


def user_character(player, cid) -> RUserCharacter:
    response = player.session.get(f"https://tinygrail.com/api/chara/user/{cid}")
    jso = snaky(response.json())
    obj = from_dict(RUserCharacter, jso)
    return obj


def blueleaf_chara_all(player) -> RBlueleafCharaAll:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/1")
    jso = snaky(response.json())
    length = from_dict(RBlueleafCharaAll, jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/user/chara/blueleaf/1/{length}")
    jso2 = snaky(resp2.json())
    lst = from_dict(RBlueleafCharaAll, jso2)
    return lst


def chara_charts(player, cid) -> RCharts:
    response = player.session.get(f"https://tinygrail.com/api/chara/charts/{cid}/2019-08-08")
    jso = snaky(response.json())
    obj = from_dict(RCharts, jso)
    return obj


def all_asks(player: Player) -> List[TCharacter]:
    # get list length
    response = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/1")
    jso = snaky(response.json())
    length = from_dict(RAllAsks, jso).value.total_items
    # get full list
    resp2 = player.session.get(f"https://tinygrail.com/api/chara/asks/0/1/{length}")
    jso2 = snaky(resp2.json())
    lst = from_dict(RAllAsks, jso2).value.items
    return lst
