from tinygrail.api import *


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def pv(player, cid) -> Tuple[int, str, float]:
    price = character_auction(player, cid).price
    chara_info = character_info(player, cid).value
    assert isinstance(chara_info, TCharacter)
    value = chara_info.rate
    return chara_info.character_id, chara_info.name, value / price


def main():
    from accounts import tg_xsb_player

    result = []

    all_holdings = all_holding_ids(tg_xsb_player)

    for n, cid in enumerate(all_holdings):
        print(f"fetching {n+1}/{len(all_holdings)}: {cid}", end="\r")
        r = pv(tg_xsb_player, cid)
        result.append(r)

    result = sorted(result, key=lambda tup: tup[2])

    for tup in result:
        print(*tup)


if __name__ == '__main__':
    main()
