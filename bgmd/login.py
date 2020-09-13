from functools import lru_cache
from typing import Optional

import requests

from bgmd.model import *


class Login:
    cfduid: str
    chii_auth: str
    _gh: str
    ua: str  # BGM copy session way seems UA-related
    user: Optional[User]

    def __init__(self, *, cfduid, chii_auth, gh=None, ua, user=None):
        self.cfduid = cfduid
        self.chii_auth = chii_auth
        self._gh = gh
        self.ua = ua
        self.user = user

    @property
    def gh(self):
        if self._gh is None:
            from bgmd.api import get_gh
            self._gh = get_gh(self)
        return self._gh

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