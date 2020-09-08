import http.cookies
from typing import *

import aiohttp
import requests
from pydantic import BaseModel, ValidationError

_MT = TypeVar("_MT", bound=BaseModel)

__all__ = ['APIResponseSchemeNotMatch', 'Player']


class APIResponseSchemeNotMatch(ValueError):
    def __init__(self, response, data):
        self.response = response
        self.data = data


class Player:
    identity: str
    on_identity_refresh: List[Callable[[str], None]]
    _session: Optional[requests.Session]
    _aio_session: Optional[aiohttp.ClientSession]

    def __init__(self, identity, on_identity_refresh=None):
        self.identity = identity
        self.on_identity_refresh = []
        if callable(on_identity_refresh):
            self.on_identity_refresh.append(on_identity_refresh)
        self._session = None
        self._aio_session = None

    def _update_identity_with_response(self, r: requests.Response, *args, **kwargs):
        new_identity = r.cookies.get('.AspNetCore.Identity.Application', domain='tinygrail.com')
        if new_identity is not None:
            self.identity = new_identity
            for f in self.on_identity_refresh:
                f(new_identity)

    @property
    def session(self):
        if self._session is not None:
            return self._session

        session = requests.Session()

        session.cookies['.AspNetCore.Identity.Application'] = self.identity

        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.7,en-US;q=0.3',
            'Content-Type': 'application/json',
            'Origin': 'https://bgm.tv',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://bgm.tv/rakuen/topiclist',
        }

        session.hooks['response'].append(self._update_identity_with_response)

        self._session = session

        return session

    @overload
    def get_data(self, url, as_model: Type[_MT], **kwargs) -> _MT:
        pass

    @overload
    def get_data(self, url, **kwargs) -> dict:
        pass

    def get_data(self, url, as_model: Type[_MT] = None, **kwargs) -> _MT:
        kwargs.setdefault('timeout', 10)
        response = self.session.get(url, **kwargs)
        data = response.json()
        if as_model is None:
            return data
        try:
            return as_model(**data)
        except ValidationError:
            raise APIResponseSchemeNotMatch(response, data)

    @overload
    def post_data(self, url, data, as_model: Type[_MT], **kwargs) -> _MT:
        pass

    @overload
    def post_data(self, url, data, **kwargs) -> dict:
        pass

    def post_data(self, url, data=None, as_model=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('json', data)
        response = self.session.get(url, **kwargs)
        data = response.json()
        if as_model is None:
            return data
        try:
            return as_model(**data)
        except ValidationError:
            raise APIResponseSchemeNotMatch(response, data)

    @property
    def aio_session(self):
        if self._aio_session is not None:
            return self._aio_session

        session = aiohttp.ClientSession(
            cookies=http.cookies.SimpleCookie({'.AspNetCore.Identity.Application': self.identity}))

        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.7,en-US;q=0.3',
            'Content-Type': 'application/json',
            'Origin': 'https://bgm.tv',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://bgm.tv/rakuen/topiclist',
        }

        self._aio_session = session

        return session
