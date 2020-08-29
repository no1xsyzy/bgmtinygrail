#!/usr/bin/env python3

from bgmd.api import *
from bgmd.model import Login
from tinygrail.api import *
from tinygrail.model import Player


def compare_asks_collect(player: Player, login: Login):
    asks = {c.character_id for c in all_asks(player)}
    favorite_characters = {c.id for c in user_mono(login.user, 'character')}

    return asks - favorite_characters, favorite_characters - asks


def sync_asks_collect(player: Player, login: Login, sets=True, logs=lambda x: None):
    anf, fna = compare_asks_collect(player, login)

    for i in anf:
        logs(f"- https://bgm.tv/character/{i}")
        if sets:
            collect_mono(login, i)

    for i in fna:
        logs(f"- https://bgm.tv/character/{i}")
        if sets:
            erase_collect_mono(login, i)
