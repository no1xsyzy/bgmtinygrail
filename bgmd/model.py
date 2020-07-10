from pydantic import BaseModel
from functools import lru_cache
from typing import *
import requests

__all__ = ['User', 'Login',
           'MonoBase', 'Images', 'Mono',
           'Character', 'Person']


class User(BaseModel):
    id: int
    url: str
    username: str
    nickname: str


class Images(BaseModel):
    large: Optional[str]
    medium: Optional[str]
    small: Optional[str]
    grid: Optional[str]


class MonoBase(BaseModel):
    id: int
    url: Optional[str]
    name: Optional[str]
    images: Optional[Images]

    def is_detail(self):
        return (self.url is not None and
                self.name is not None and
                self.images is not None)


class Mono(MonoBase):
    name_cn: Optional[str]
    comment: Optional[int]
    collects: Optional[int]

    def is_detail(self):
        return (super().is_detail() and
                self.name_cn is not None and
                self.comment is not None and
                self.collects is not None)


class Character(Mono):
    def __eq__(self, other):
        return isinstance(other, Character) and other.id == self.id


class Person(Mono):
    def __eq__(self, other):
        return isinstance(other, Person) and other.id == self.id


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
