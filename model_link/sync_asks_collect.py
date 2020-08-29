#!/usr/bin/env python3
import logging.config

from accounts import bgm_xsb_player, tg_xsb_player
from bgmd.api import *
from bgmd.model import Login
from tinygrail.api import *
from tinygrail.model import Player

logger = logging.getLogger('check_all_selling')


def sync_asks_collect(player: Player, login: Login, sets=True):
    asks = {c.character_id for c in all_asks(player)}

    favorite_characters = {c.id for c in user_mono(login.user, 'character')}

    for i in asks - favorite_characters:
        print(f"+ https://bgm.tv/character/{i}")
        if sets:
            collect_mono(login, i)

    for i in favorite_characters - asks:
        print(f"- https://bgm.tv/character/{i}")
        if sets:
            erase_collect_mono(login, i)


if __name__ == "__main__":
    logging.config.fileConfig('../logging.conf')
    sync_asks_collect(tg_xsb_player, bgm_xsb_player, True)
