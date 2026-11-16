import sqlite3
from flask import current_app, g

import config


def get_db():
    """リクエストごとに1つだけDBにつなぐ"""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    """テーブルを作り、単元のデータを入れる(何回実行しても安全)"""
    con = sqlite3.connect(path)
    with open(config.BASE_DIR + "/schema.sql", encoding="utf-8") as f:
        con.executescript(f.read())
    for order_no, (unit_id, name) in enumerate(config.UNITS.items(), 1):
        con.execute(
            "INSERT OR IGNORE INTO units (unit_id, name, order_no) VALUES (?, ?, ?)",
            (unit_id, name, order_no))
    con.commit()
    con.close()
