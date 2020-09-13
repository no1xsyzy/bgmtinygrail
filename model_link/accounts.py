from typing import *

import lazy_object_proxy

from bgmd.api import user_info
from bgmd.login import Login
from db import accounts as db_accounts
from tinygrail.player import Player

__all__ = []


class LoginPlayer(NamedTuple):
    name: str
    bangumi: Login
    tinygrail: Player


def translate(dr: Dict) -> LoginPlayer:
    identity = dr.pop('tinygrail_identity')
    user = user_info(dr.pop('id'))
    name = dr.pop('friendly_name')
    bangumi = Login(**dr, user=user)

    def update_identity(new_identity):
        db_accounts.update(name, tinygrail_identity=new_identity)

    tinygrail = Player(identity, on_identity_refresh=update_identity)
    return LoginPlayer(name, bangumi, tinygrail)


all_accounts: Dict[str, LoginPlayer] = {}

for friendly_name in db_accounts.list_all():
    for dict_row in db_accounts.retrieve(friendly_name):
        globals()[friendly_name] = all_accounts[friendly_name] = lazy_object_proxy.Proxy(
            (lambda dr: lambda: translate(dr))(dict_row))
        __all__.append(friendly_name)
