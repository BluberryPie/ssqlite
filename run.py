import ssqlite


def main():
    ssqlite.executescript(db_name="test.db", sql_filename="test_delete.sql")


if __name__ == "__main__":  
    main()
