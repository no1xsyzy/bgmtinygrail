from typing import Tuple, Dict

from sqlalchemy import ForeignKey
from sqlalchemy.orm.exc import NoResultFound

from ._base import *


class CharacterStrategy(MainBase):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, nullable=False)
    username = Column(String(64), ForeignKey('accounts.friendly_name'), nullable=False)
    strategy_id = Column(Integer, nullable=False)
    kwargs = Column(String, nullable=False)  # json

    def __repr__(self):
        return (f"<CharacterStrategy(character_id={self.character_id!r}, username={self.username!r}, "
                f"strategy_id={self.strategy_id!r}, kwargs={self.kwargs!r})>")


@auto_session(DbMainSession)
def set_strategy(character_id: int, username: str, strategy_id: int, kwargs: str, *, session):
    try:
        the_strategy: CharacterStrategy = session.query(CharacterStrategy) \
            .filter_by(character_id=character_id, username=username).one()
        the_strategy.strategy_id = strategy_id
        the_strategy.kwargs = kwargs
    except NoResultFound:
        the_strategy = CharacterStrategy(character_id=character_id, username=username,
                                         strategy_id=strategy_id, kwargs=kwargs)
        session.add(the_strategy)


@auto_session(DbMainSession, writes=False)
def get_strategy(character_id: int, username: str, *, session=None) -> Tuple[int, str]:
    return session.query(CharacterStrategy.strategy_id, CharacterStrategy.kwargs) \
        .filter_by(character_id=character_id, username=username).one()


@auto_session(DbMainSession)
def purge_strategy(character_id: int, username: str, *, session=None):
    the_strategy: CharacterStrategy = session.query(CharacterStrategy) \
        .filter_by(character_id=character_id, username=username).one()
    session.delete(the_strategy)


@auto_session(DbMainSession)
def loads_strategy(username: str, *, session=None) -> Dict[int, Tuple[int, str]]:
    result = {}
    for cid, sid, kwargs in session.query(
            CharacterStrategy.character_id,
            CharacterStrategy.strategy_id,
            CharacterStrategy.kwargs
    ).filter_by(username=username):
        result[cid] = sid, kwargs
    return result
