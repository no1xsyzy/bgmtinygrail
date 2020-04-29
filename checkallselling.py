#!/usr/bin/env python3
from bgmd.api import *
from accounts import bgm_xsb_player, tg_xsb_player
from tinygrail.api import *

asks = {c.character_id for c in all_asks(tg_xsb_player)}

favorite_characters = {c.id for c in user_mono(user_info(username='525688'), 'character')}

for i in asks - favorite_characters:
    print(f"+ https://bgm.tv/character/{i}")
    collect_mono(bgm_xsb_player, i)

for i in favorite_characters - asks:
    print(f"- https://bgm.tv/character/{i}")
    erase_collect_mono(bgm_xsb_player, i)
