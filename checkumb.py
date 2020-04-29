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

# edits, from code in page:
# ```javascript
# console.log(`followed = "${JSON.parse(localStorage.getItem('TinyGrail_followList'))['charas'].join("|")}"`)
# ```

checklist: Set[int] = umb_characters - {cid for cid in (follow_list + umb_temple_list + umb_ignore_list)}

print("\n".join(f"https://bgm.tv/character/{chara.character_id}"
                for chara in batch_character_info(no1xsyzy, checklist)))
