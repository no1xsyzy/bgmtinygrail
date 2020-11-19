from datetime import timedelta, datetime

from ._base import *


class BgmCharacter(CacheBase):
    __tablename__ = 'character_of'

    id = Column(Integer, primary_key=True)
    cache_token = Column(String(16))
    # cache_token examples:
    # cv/5076
    # sub/123123
    content = Column(Text)
    last_refreshed = Column(DateTime)


@auto_session(DbCacheSession)
def get(token, *, session=None, expires=timedelta(weeks=4)):
    try:
        row = session.query(BgmCharacter).filter_by(cache_token=token).one()
        if row.last_refreshed + expires < datetime.now():
            session.delete(row)
            return None
        return [int(s_cid) for s_cid in row.content.split("|")]
    except NoResultFound:
        return None


@auto_session(DbCacheSession)
def put(token, characters, *, session=None):
    row = BgmCharacter(
        cache_token=token,
        content='|'.join(str(cid) for cid in characters),
        last_refreshed=datetime.now()
    )
    session.add(row)
