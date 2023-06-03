import ssqlite

from ssqlite.recovery import generate_undo_query


def main():
    ssqlite.executescript(db_name="test.db", sql_filename="test_insert.sql")
    undo_query = generate_undo_query(query_idx=6)
    print(f"{undo_query = }")


if __name__ == "__main__":

    QUERIES = [
        {1: "CREATE TABLE X (id INTEGER PRIMARY KEY, name VARCHAR(255));"},
        {2: "INSERT INTO X(id, name) VALUES(1, 'Alice');"},
        {3: "INSERT INTO X(id, name) VALUES(2, 'Bob');"},
        {4: "UPDATE X SET name='April' WHERE id=1;"},
        {5: "UPDATE X SET name='Aaron' WHERE id=1;"},
        {6: "DELETE FROM X WHERE name='Aaron';"}, # target
        {7: "INSERT INTO X(id, name) VALUES(3, 'Charles');"},
        {8: "INSERT INTO X(id, name) VALUES(4, 'David');"},
        {9: "UPDATE X SET name='Brendan' WHERE id=2;"},
        {10: "UPDATE X SET name='Danielle' WHERE name='David';"},
        {11: "INSERT INTO X(id, name) VALUES(5, 'Eve');"},
        {12: "INSERT INTO X(id, name) VALUES(6, 'Francis');"},
        {13: "DELETE FROM X WHERE id=4;"},
        {14: "INSERT INTO X(id, name) VALUES(7, 'Gerrard');"}
    ]
    main()
