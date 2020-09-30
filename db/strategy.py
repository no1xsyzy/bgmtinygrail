from typing import Tuple, Any

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


def set_strategy(character_id, username, strategy_id, kwargs: Any, *, session=None):
    if session is None:
        try:
            session = DbMainSession()
            return set_strategy(character_id, username, strategy_id, kwargs, session=session)
        except:
            session.rollback()
            raise
        finally:
            session.commit()
            session.close()

    try:
        the_strategy: CharacterStrategy = session.query(CharacterStrategy) \
            .filter_by(character_id=character_id, username=username).one()
        the_strategy.strategy = strategy_id
        the_strategy.kwargs = kwargs
    except NoResultFound:
        the_strategy = CharacterStrategy(character_id=character_id, username=username,
                                         strategy_id=strategy_id, kwargs=kwargs)
        session.add(the_strategy)


def get_strategy(character_id, username, *, session=None) -> Tuple[int, Any]:
    if session is None:
        try:
            session = DbMainSession()
            return get_strategy(character_id, username, session=session)
        finally:
            session.close()

    return session.query(CharacterStrategy.strategy_id, CharacterStrategy.kwargs) \
        .filter_by(character_id=character_id, username=username).one()
