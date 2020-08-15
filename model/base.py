import sqlite3
from pathlib import Path
from typing import *

db: Optional[sqlite3.Connection] = None


def check_db_rev(db):
    try:
        return db.execute("SELECT rev FROM db_rev").fetchone()[0]
    except sqlite3.OperationalError:
        return 0


def get_db():
    global db
    if db is None:
        db = sqlite3.connect(
            Path("tinygrail.db"),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        current_path = Path(__file__).parent.absolute()
        while True:
            db_rev = check_db_rev(db)
            try:
                with (current_path / f"schema-update-from-{db_rev}.sql").open(encoding="utf-8") as f:
                    db.executescript(f.read())
            except FileNotFoundError:
                assert db_rev == 1
                break
    return db


def close_db(e=None):
    global db
    if db is not None:
        db.close()
    db = None
