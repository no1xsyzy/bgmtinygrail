#!/usr/bin/env python3
from tinygrail.api import *
from data import *
from accounts import *

print("\n".join(f"https://bgm.tv/character/{chara.character_id}"
                for chara in batch_character_info(tg_xsb_player, waitlist)))
