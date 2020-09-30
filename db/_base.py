from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


__all__ = ['DbMainSession', 'DbCacheSession', 'DbRuntimeSession',
           'MainBase', 'CacheBase', 'RuntimeBase',
           'Column', 'Integer', 'String',
           'create_all']
