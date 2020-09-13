from pydantic import BaseModel
from typing import *

__all__ = ['User', 'MonoBase', 'Images', 'Mono',
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


