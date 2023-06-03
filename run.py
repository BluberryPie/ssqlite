import ssqlite


def main():
    # Example code
    ssqlite.executescript(
        db_name="test.db",
        sql_filename="test.sql",
        sqg_filename="test.sqg"
    )


if __name__ == "__main__":

    main()
