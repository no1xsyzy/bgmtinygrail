from typing import Type

import requests
from pydantic import BaseModel, ValidationError


class APIResponseSchemeNotMatch(ValueError):
    def __init__(self, response, data):
        self.response = response
        self.data = data


def as_model(self, model: Type[BaseModel]):
    data = self.json()
    try:
        return model(**data)
    except ValidationError:
        raise APIResponseSchemeNotMatch(self, data)


def monkey_patch():
    requests.Response.as_model = as_model
