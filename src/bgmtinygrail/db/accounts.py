from typing import List

from ._base import *


class Account(MainBase):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    friendly_name = Column(String(64), index=True, nullable=False, unique=True)
    chii_auth = Column(String(128), nullable=False)
    ua = Column(String(128), nullable=False)
    tinygrail_identity = Column(String(1000), nullable=False)

    def __repr__(self):
        return (f"<Accounts(friendly_name={self.friendly_name!r}, id={self.id!r}, "
                f"chii_auth={self.chii_auth!r}, ua={self.ua!r}, "
                f"tinygrail_identity={self.tinygrail_identity!r})>")


@auto_session(DbMainSession)
def create(friendly_name: str, uid: int,
           chii_auth: str, ua: str,
           tinygrail_identity: str, *, session=None):
    new_acc = Account(id=uid, friendly_name=friendly_name,
                      chii_auth=chii_auth, ua=ua,
                      tinygrail_identity=tinygrail_identity)
    session.add(new_acc)


@auto_session(DbMainSession, writes=False)
def retrieve(friendly_name: str, *, session: DbMainSession = None) -> Account:
    return session.query(Account).filter_by(friendly_name=friendly_name).one()


@auto_session(DbMainSession)
def update(friendly_name: str, *, session=None, **kwargs):
    obj = session.query(Account).filter_by(friendly_name=friendly_name)
    for k, v in kwargs.items():
        setattr(obj, k, v)


@auto_session(DbMainSession)
def delete(friendly_name: str, *, session=None):
    obj = session.query(Account).filter_by(friendly_name=friendly_name)
    session.delete(obj)


@auto_session(DbMainSession, writes=False)
def list_all(*, session=None) -> List[str]:
    if session is None:
        try:
            session = DbMainSession()
            return list_all(session=session)
        finally:
            session.close()

    return [friendly_name[0] for friendly_name in session.query(Account.friendly_name)]
