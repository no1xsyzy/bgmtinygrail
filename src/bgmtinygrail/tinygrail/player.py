import http.cookies
from typing import *

import aiohttp
import requests
from pydantic import BaseModel, ValidationError

from .model import RErrorMessage

_MT = TypeVar("_MT", bound=BaseModel)

__all__ = ['APIResponseSchemeNotMatch', 'ServerNotReachable', 'ServerSentError', 'Player']


class APIResponseSchemeNotMatch(ValueError):
    def __init__(self, response, data):
        self.response = response
        self.data = data


class ServerNotReachable(IOError):
    def __init__(self, status_code):
        self.status_code = status_code


class ServerSentError(Exception):
    def __init__(self, state, message):
        self.state = state
        self.message = message


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
            'User-Agent': 'bgmtinygrail/ea',
            'Content-Type': 'application/json',
        }

        session.hooks['response'].append(self._update_identity_with_response)

        self._session = session

        return session

    def _process_response(self, response, *, as_model: Type[_MT] = None):
        if 500 <= response.status_code < 600:
            raise ServerNotReachable(response.status_code)
        new_identity = response.cookies.get('.AspNetCore.Identity.Application', domain='tinygrail.com')
        if new_identity is not None:
            self.identity = new_identity
            for f in self.on_identity_refresh:
                f(new_identity)

        try:
            rd = response.json()
        except JSONDecodeError:
            raise APIResponseSchemeNotMatch(response, None) from None

        if as_model is None:
            return rd
        try:
            return as_model(**rd)
        except ValidationError:
            try:
                err_msg = RErrorMessage(**rd)
                raise ServerSentError(err_msg.state, err_msg.message) from None
            except ValidationError:
                raise APIResponseSchemeNotMatch(response, rd) from None

    @overload
    def get_data(self, url, as_model: Type[_MT], **kwargs) -> _MT:
        pass

    @overload
    def get_data(self, url, as_model: None, **kwargs) -> dict:
        pass

    def get_data(self, url, as_model: Type[_MT] = None, **kwargs) -> _MT:
        kwargs.setdefault('timeout', 10)
        response = self.session.get(url, **kwargs)
        return self._process_response(response, as_model=as_model)

    @overload
    def post_data(self, url, data, as_model: Type[_MT], **kwargs) -> _MT:
        pass

    @overload
    def post_data(self, url, data, as_model: None, **kwargs) -> dict:
        pass

    def post_data(self, url, data=None, as_model: Type[_MT] = None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('json', data)
        response = self.session.post(url, **kwargs)
        return self._process_response(response, as_model=as_model)

    @property
    def aio_session(self):
        if self._aio_session is not None:
            return self._aio_session

        session = aiohttp.ClientSession(
            cookies=http.cookies.SimpleCookie({'.AspNetCore.Identity.Application': self.identity}),
            headers={
                'User-Agent': 'bgmtinygrail/beta',
                'Content-Type': 'application/json',
            }
        )

        self._aio_session = session

        return session
