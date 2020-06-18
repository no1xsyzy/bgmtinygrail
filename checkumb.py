#!/usr/bin/env python3
import requests
import re
from bs4 import BeautifulSoup
from typing import *
from tinygrail.api import batch_character_info
from bgmd.api import person_work_voice_character
from bgmd.model import *
from accounts import no1xsyzy
from data import *


aoi_chan = Person(5076)

umb_characters: Set[int] = {c.id for c in person_work_voice_character(aoi_chan)}

temples = user_temples(no1xsyzy)
temple_list = [t.character_id for t in temples if t.assets >= 2500]

checklist: Set[int] = umb_characters - {cid for cid in (follow_list + umb_temple_list + umb_ignore_list)}

print("\n".join(f"https://bgm.tv/character/{chara.character_id}"
                for chara in batch_character_info(no1xsyzy, checklist)))
