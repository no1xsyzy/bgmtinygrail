from typing import *

import aiohttp
import requests
from pydantic import BaseModel
from requests import Response

_MT = TypeVar("_MT", bound=BaseModel)


class APIResponseSchemeNotMatch(ValueError):
    response: Response
    data: Optional[Any]


class ServerNotReachable(IOError):
    status_code: int


class ServerSentError(Exception):
    state: int
    message: str


class Player:
    identity: str
    on_identity_refresh: List[Callable[[str], None]]
    _session: Optional[requests.Session]
    _aio_session: Optional[aiohttp.ClientSession]

    def __init__(self, identity: str, on_identity_refresh: Callable[[str], None] = None): ...

    @property
    def session(self) -> requests.Session: ...

    @overload
    def _process_response(self, response: Response, *, as_model: Type[_MT]) -> _MT: ...

    @overload
    def _process_response(self, response: Response, *, as_model: None = None) -> dict: ...

    @overload
    def get_data(self, url: str, as_model: Type[_MT], **kwargs) -> _MT: ...

    @overload
    def get_data(self, url: str, as_model: None = None, **kwargs) -> dict: ...

    @overload
    def post_data(self, url, data, as_model: Type[_MT], **kwargs) -> _MT: ...

    @overload
    def post_data(self, url, data, as_model: None = None, **kwargs) -> dict: ...

    @property
    def aio_session(self) -> aiohttp.ClientSession: ...
