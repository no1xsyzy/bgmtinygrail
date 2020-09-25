from inflection import camelize
from pydantic import BaseModel


class TinygrailModel(BaseModel):
    class Config:
        alias_generator = camelize
