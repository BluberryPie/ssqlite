import sqlite3

from ssqlite.algo import build_sqg_from_sql


def executescript(db_name: str, sql_filename: str):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    build_sqg_from_sql(cursor, sql_filename)
