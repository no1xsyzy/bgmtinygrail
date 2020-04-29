#!/usr/bin/env python3
from tinygrail.api import *
from data import *

print("\n".join(f"https://bgm.tv/character/{chara.character_id}"
                for chara in batch_character_info(waitlist)))
