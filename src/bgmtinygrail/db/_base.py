from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

engine_main = create_engine('sqlite:///tinygrail.db')
engine_cache = create_engine('sqlite:///cache.db')
engine_runtime = create_engine('sqlite://')

MainBase = declarative_base()
CacheBase = declarative_base()
RuntimeBase = declarative_base()

DbMainSession = sessionmaker(bind=engine_main)
DbCacheSession = sessionmaker(bind=engine_cache)
DbRuntimeSession = sessionmaker(bind=engine_runtime)


def create_all():
    MainBase.metadata.create_all(engine_main)
    CacheBase.metadata.create_all(engine_cache)
    RuntimeBase.metadata.create_all(engine_runtime)


def auto_session(session_cls, *,
                 writes: bool = True, commits: bool = None, rollbacks: bool = None,
                 closes: bool = True):
    if rollbacks is None:
        rollbacks = writes
    if commits is None:
        commits = writes

    def wrapper(func):
        from functools import wraps

        @wraps(func)
        def wrapped(*args, session=None, **kwargs):
            if session is not None:
                return func(*args, session=session, **kwargs)
            try:
                session = session_cls()
                return func(*args, session=session, **kwargs)
            except:
                if rollbacks:
                    session.rollback()
                raise
            finally:
                if commits:
                    session.commit()
                if closes:
                    session.close()

        return wrapped

    return wrapper


__all__ = ['DbMainSession', 'DbCacheSession', 'DbRuntimeSession',
           'MainBase', 'CacheBase', 'RuntimeBase',
           'Column', 'Integer', 'String', 'Text', 'DateTime',
           'ForeignKey',
           'NoResultFound',
           'create_all', 'auto_session']
