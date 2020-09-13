from functools import lru_cache
from typing import Optional

import requests

from bgmd.model import *


class Login:
    cfduid: str
    chii_auth: str
    gh: str
    ua: str  # BGM copy session way seems UA-related
    user: Optional[User]

    def __init__(self, cfduid, chii_auth, gh, ua, user=None):
        self.cfduid = cfduid
        self.chii_auth = chii_auth
        self.gh = gh
        self.ua = ua
        self.user = user

    @property
    @lru_cache
    def session(self) -> requests.Session:
        sess = requests.Session()

        sess.cookies['chii_theme'] = 'light'
        sess.cookies['__cfduid'] = self.cfduid
        sess.cookies['chii_cookietime'] = '0'
        sess.cookies['chii_auth'] = self.chii_auth
        sess.headers['User-Agent'] = self.ua

        return sess