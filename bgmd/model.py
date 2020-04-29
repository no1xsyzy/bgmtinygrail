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
    user: Optional[User]

    @property
    @lru_cache
    def session(self) -> requests.Session:
        sess = requests.Session()

        sess.cookies['chii_theme'] = 'light'
        sess.cookies['__cfduid'] = self.cfduid
        sess.cookies['chii_cookietime'] = '0'
        sess.cookies['chii_auth'] = self.chii_auth

        sess.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'

        sess.proxies['https'] = "http://localhost:1081"

        return sess
