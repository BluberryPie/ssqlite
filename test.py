import os
import ssqlite
import unittest

from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.recovery import generate_undo_query


class RecoveryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        query_types = ["create", "insert", "update", "drop", "delete"]
        for query_type in query_types:
            if os.path.exists(f"{query_type}.db"):
                os.remove(f"{query_type}.db")
            if os.path.exists(f"{query_type}.sqg"):
                os.remove(f"{query_type}.sqg")
    
    @classmethod
    def tearDownClass(cls) -> None:
        query_types = ["create", "insert", "update", "drop", "delete"]
        for query_type in query_types:
            if os.path.exists(f"{query_type}.db"):
                os.remove(f"{query_type}.db")
            if os.path.exists(f"{query_type}.sqg"):
                os.remove(f"{query_type}.sqg")
    
    def get_undo_query(
            self, db_name: str, sql_filename: str,
            sqg_filename: str, query_order: int
        ) -> list[str]:
        """Helper function for generating undo query sets"""
        ssqlite.executescript(
            db_name=db_name,
            sql_filename=sql_filename,
            sqg_filename=sqg_filename
        )
        graph = SQG.load_from_file(sqg_filename)
        undo_query_set = generate_undo_query(graph, query_order=query_order)
        return undo_query_set

    def test_recovery_create(self):
        undo_query_set = self.get_undo_query(
            db_name="create.db",
            sql_filename="test_create.sql",
            sqg_filename="create.sqg",
            query_order=1 # CREATE TABLE X (id INTEGER PRIMARY KEY, name VARCHAR(255));
        )
        expected_query_set = [
            "DROP TABLE X;"
        ]
        self.assertEqual(
            [query.lower() for query in undo_query_set],
            [query.lower() for query in expected_query_set]
        )

    def test_recovery_insert(self):
        undo_query_set = self.get_undo_query(
            db_name="insert.db",
            sql_filename="test_insert.sql",
            sqg_filename="insert.sqg",
            query_order=4 # INSERT INTO X(id, name) VALUES(3, 'Charles');
        )
        expected_query_set = [
            "DELETE FROM X WHERE rowid=3;"
        ]
        self.assertEqual(
            [query.lower() for query in undo_query_set],
            [query.lower() for query in expected_query_set]
        )

    def test_recovery_update(self):
        undo_query_set = self.get_undo_query(
            db_name="update.db",
            sql_filename="test_update.sql",
            sqg_filename="update.sqg",
            query_order=9 # UPDATE X SET name='Brendan' WHERE id=2;
        )
        expected_query_set = [
            "DELETE FROM X WHERE rowid=2;",
            "INSERT INTO X(id, name) VALUES(2, 'Bob');"
        ]
        self.assertEqual(
            [query.lower() for query in undo_query_set],
            [query.lower() for query in expected_query_set]
        )

    def test_recovery_drop(self):
        undo_query_set = self.get_undo_query(
            db_name="drop.db",
            sql_filename="test_drop.sql",
            sqg_filename="drop.sqg",
            query_order=15 # DROP TABLE X;
        )
        expected_query_set = [
            "CREATE TABLE X (id INTEGER PRIMARY KEY, NAME VARCHAR(255));",
            "INSERT INTO X(id, name) VALUES(2, 'Bob');",
            "INSERT INTO X(id, name) VALUES(3, 'Charles');",
            "INSERT INTO X(id, name) VALUES(5, 'Eve');",
            "INSERT INTO X(id, name) VALUES(6, 'Francis');",
            "INSERT INTO X(id, name) VALUES(7, 'Gerrard');",
            "UPDATE X SET name='Brendan' WHERE ID=2;"
        ]
        self.assertEqual(
            [query.lower() for query in undo_query_set],
            [query.lower() for query in expected_query_set]
        )

    def test_recovery_delete(self):
        undo_query_set = self.get_undo_query(
            db_name="delete.db",
            sql_filename="test_delete.sql",
            sqg_filename="delete.sqg",
            query_order=6 # DELETE FROM X WHERE name='Aaron';
        )
        expected_query_set = [
            "INSERT INTO X(id, name) VALUES(1, 'Alice');",
            "UPDATE X SET name='Aaron' WHERE id=1;"
        ]
        self.assertEqual(
            [query.lower() for query in undo_query_set],
            [query.lower() for query in expected_query_set]
        )


if __name__ == "__main__":

    unittest.main()
