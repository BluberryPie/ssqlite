import ssqlite

from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.recovery import generate_undo_query


def main():
    ssqlite.executescript(
        db_name="test.db",
        sql_filename="test.sql",
        sqg_filename="test.sqg"
    )


if __name__ == "__main__":

    main()
