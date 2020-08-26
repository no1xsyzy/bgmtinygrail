from .base import get_db


def create(friendly_name, uid, cfduid, chii_auth, gh, ua, tinygrail_identity):
    exists = bool(
        get_db().execute("""
            SELECT 
                friendly_name 
            FROM 
                accounts 
            WHERE 
                friendly_name=? 
            LIMIT 1
        """, (friendly_name,)).fetchall()
    )
    if exists:
        return f"Account {friendly_name} has already been added"
    db = get_db()
    db.execute("""
        INSERT INTO accounts
            (friendly_name, id, cfduid, chii_auth, gh, ua, tinygrail_identity) 
        VALUES
            (?, ?, ?, ?, ?, ?, ?)""", (friendly_name, uid, cfduid, chii_auth, gh, ua, tinygrail_identity))
    db.commit()


def retrieve(friendly_name):
    res = get_db().execute("""
        SELECT
            friendly_name, id, cfduid, chii_auth, gh, ua, tinygrail_identity
        FROM
            accounts
        WHERE
            friendly_name=?
    """, (friendly_name,))
    return [dict(row) for row in res]


def update(friendly_name, **kwargs):
    ks = []
    vs = []
    for k, v in kwargs.items():
        ks.append(k)
        vs.append(v)
    assert len(ks) == len(vs)
    db = get_db()
    db.execute(f"""
        UPDATE accounts
        SET ({",".join(k + "=?" for k in ks)})
        WHERE friendly_name=?
    """, (*vs, friendly_name))
    db.commit()


def delete(friendly_name):
    db = get_db()
    db.execute("""
        DELETE FROM accounts
        WHERE friendly_name=?
    """, (friendly_name,))
    db.commit()


def list_all():
    res = get_db().execute("""
        SELECT
            friendly_name
        FROM
            accounts
    """)
    return [row[0] for row in res]
