from typing import Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError

_MT = TypeVar("_MT", bound=BaseModel)


class APIResponseSchemeNotMatch(ValueError):
    def __init__(self, response, data):
        self.response = response
        self.data = data


def as_model(self: requests.Response, model: Type[_MT]) -> _MT:
    data = self.json()
    try:
        return model(**data)
    except ValidationError:
        raise APIResponseSchemeNotMatch(self, data)


def monkey_patch():
    requests.Response.as_model = as_model
