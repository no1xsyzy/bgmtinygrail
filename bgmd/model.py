from dataclasses import dataclass
from functools import lru_cache
from typing import *
import requests

__all__ = ['User', 'Mono', 'Character', 'Person', 'Login']


@dataclass(frozen=True)
class User:
    id: int
    url: str
    username: str
    nickname: str


@dataclass(frozen=True)
class Mono:
    id: int


@dataclass(frozen=True)
class Character(Mono):
    pass


@dataclass(frozen=True)
class Person(Mono):
    pass


@dataclass(frozen=True)
class Login:
    cfduid: str
    chii_auth: str
    gh: str
    ua: str  # BGM copy session way seems UA-related
    user: Optional[User]

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
