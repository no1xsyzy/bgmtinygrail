from datetime import timedelta, datetime
from typing import Union, Optional, List

from ._base import *


class BgmCharacter(CacheBase):
    id: int
    cache_token: str
    content: str
    last_refreshed: datetime


def get(
        token: str,
        *,
        session: Optional[DbCacheSession] = None,
        expires: timedelta = timedelta(weeks=4),
) -> Union[None, List[int]]: ...


def put(token: str, characters: List[int], *, session: Optional[DbCacheSession] = None): ...
