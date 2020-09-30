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


def translate(acc: db_accounts.Account) -> LoginPlayer:
    user = user_info(acc.id)
    bangumi = Login(chii_auth=acc.chii_auth, ua=acc.ua, user=user)

    def update_identity(new_identity):
        db_accounts.update(acc.friendly_name, tinygrail_identity=new_identity)

    tinygrail = Player(acc.tinygrail_identity, on_identity_refresh=update_identity)
    return LoginPlayer(acc.friendly_name, bangumi, tinygrail)


all_accounts: Dict[str, LoginPlayer] = {}

for friendly_name in db_accounts.list_all():
    account = db_accounts.retrieve(friendly_name)
    globals()[friendly_name] = all_accounts[friendly_name] = lazy_object_proxy.Proxy(
        (lambda acc: lambda: translate(acc))(account))
    __all__.append(friendly_name)
