#!/usr/bin/env python3
from typing import *

from dacite.exceptions import MissingValueError

from accounts import no1xsyzy
from bgmd.api import person_work_voice_character
from bgmd.model import *
from data import *
from tinygrail.api import batch_character_info, user_temples


def main():
    try:
        aoi_chan = Person(5076)
        umb_characters: Set[int] = {c.id for c in person_work_voice_character(aoi_chan)}
        temples = user_temples(no1xsyzy)
        temple_list = [t.character_id for t in temples if t.assets >= 2500]
        checklist: Set[int] = umb_characters - {cid for cid in (follow_list + temple_list + umb_ignore_list)}
        print("\n".join(f"https://bgm.tv/character/{chara.character_id}"
                        for chara in batch_character_info(no1xsyzy, checklist)))
    except MissingValueError:
        import inspect
        from pprint import pprint
        original_data = inspect.trace()[-1][0].f_locals['data']
        pprint(original_data)


if __name__ == '__main__':
    main()
