from dataclasses import dataclass, field
from functools import lru_cache
from typing import *
import requests

__all__ = ['User', 'Login',
           'MonoBase', 'Images', 'Mono',
           'Character', 'Person']


@dataclass(frozen=True)
class User:
    id: int
    url: str
    username: str
    nickname: str


@dataclass()
class Images:
    large: Optional[str] = field(default=None)
    medium: Optional[str] = field(default=None)
    small: Optional[str] = field(default=None)
    grid: Optional[str] = field(default=None)


@dataclass(frozen=True)
class MonoBase:
    id: int
    url: Optional[str] = field(default=None, compare=False)
    name: Optional[str] = field(default=None, compare=False)
    images: Optional[Images] = field(default=None, compare=False)

    def is_detail(self):
        return (self.url is not None and
                self.name is not None and
                self.images is not None)


@dataclass(frozen=True)
class Mono(MonoBase):
    name_cn: Optional[str] = field(default=None, compare=False)
    comment: Optional[int] = field(default=None, compare=False)
    collects: Optional[int] = field(default=None, compare=False)

    def is_detail(self):
        return (super().is_detail() and
                self.name_cn is not None and
                self.comment is not None and
                self.collects is not None)


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
