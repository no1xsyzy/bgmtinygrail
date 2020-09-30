from typing import Optional
from urllib.parse import quote_plus

import requests

from bgmd.model import *


class Login:
    chii_auth: str
    _gh: str
    ua: str  # BGM copy session way seems UA-related
    user: Optional[User]
    _session: Optional[requests.Session]

    def __init__(self, *, chii_auth, gh=None, ua, user=None):
        self.chii_auth = chii_auth
        self._gh = gh
        self.ua = ua
        self.user = user
        self._session = None

    @property
    def gh(self):
        if self._gh is None:
            from bgmd.api import get_gh
            self._gh = get_gh(self)
        return self._gh

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            self._session.cookies['chii_auth'] = quote_plus(self.chii_auth)
            self._session.headers['User-Agent'] = self.ua
        return self._session
