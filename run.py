import ssqlite

from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.recovery import generate_undo_query


def main():
    ssqlite.executescript(db_name="test.db", sql_filename="test_delete.sql")

    graph = SQG.load_from_file()
    undo_query_set = generate_undo_query(graph, query_order=15) # DELETE FROM X WHERE name='Aaron';
    
    # ssqlite.executescript(db_name="test.db", sql_filename="test_insert.sql")

    # graph = SQG.load_from_file()
    # undo_query_set = generate_undo_query(graph, query_order=4) # INSERT INTO X(id, name) VALUES(3, 'Charles');
    
    print("--UNDO QUERY SET--")
    for undo_query in undo_query_set:
        print(undo_query)


if __name__ == "__main__":

    main()
