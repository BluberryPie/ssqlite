import ssqlite

from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.recovery import generate_undo_query


def main():
    ssqlite.executescript(db_name="test.db", sql_filename="test_delete.sql")

    graph = SQG.load_from_file()
    undo_query = generate_undo_query(graph, query_order=6) # DELETE FROM X WHERE name='Aaron';
    print(f"{undo_query = }")


if __name__ == "__main__":

    main()
