# ↺ SSQLite(Secure SQLite)

**`SSQLite`**, an abbreviation for Secure Sqlite, adds an additional layer to the `sqlite3` module by recording database modifications. This feature allows users to revert a specific query executed at any point in time. The logging mechanism is facilitated by a sophisticated data structure called **SSqliteQueryGraph** (SQG), which functions as a tree structure comprising nodes representing individual query statements. SQG not only tracks the queries that users intend to undo but also offers an efficient set of queries for data recovery. Consequently, users can now perform Point In Time Recovery (PITR) without executing irrelevant queries, resulting in significant savings in computing resources.

## Example

Suppose a user wants to undo a `DELETE` statement from the recorded history (6th query from the following example). This action may be prompted by an SQL injection attack, or it could just be the user's intention to rectify an erroneously inserted query from a previous point in time.

``` sql
1 CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(255));
2 INSERT INTO users(id, name) VALUES(1, 'Alice');
3 INSERT INTO users(id, name) VALUES(2, 'Bob');
4 UPDATE users SET name='April' WHERE id=1;
5 UPDATE users SET name='Aaron' WHERE id=1;
6 DELETE FROM users WHERE name='Aaron'; --> Target
7 INSERT INTO users(id, name) VALUES(3, 'Charles');
8 INSERT INTO users(id, name) VALUES(4, 'David');
9 UPDATE users SET name='Brendan' WHERE id=2;
(...and a bunch of more queries)
```

In previous approaches to performing Point In Time Recovery (PITR), it was necessary to either execute all queries preceding the target query or employ snapshot recovery methods. Subsequently, the user would need to execute all subsequent queries after the target query to maintain the most up-to-date state.

However, a more efficient approach would involve extracting only the relevant queries associated with the targeted query and generating a set of queries capable of reverting this subset of actions. In the example mentioned above, the relevant queries pertaining to the `DELETE` statement are as follows:

``` sql
2 INSERT INTO users(id, name) VALUES(1, 'Alice');
4 UPDATE users SET name='April' WHERE id=1;
5 UPDATE users SET name='Aaron' WHERE id=1;
```

The resulting "undo query set" can be represented by a single line of an INSERT statement, exemplifying how this approach can significantly conserve computational resources by skipping unnecessary actions.

``` sql
INSERT INTO users(id, name) VALUES(1, 'Aaron');
```

Unfortunately, the current version of **`SSQLite`** does not possess the ability to compress the "undo query set" in the aforementioned manner. Nonetheless, it is proficient in generating *quasi*-optimal solutions for each query statement, leading to time savings in the process. Our current version would generate the "undo query set" as the following:

``` sql
INSERT INTO X(id, name) VALUES(1, 'Alice');
UPDATE X SET name='Aaron' WHERE id=1;
```

---

## Run

A sample of running queries from a .sql file is as follows:

``` python
import ssqlite

ssqlite.executescript(
    db_name="test.db",
    sql_filename="test.sql",
    sqg_filename="test.sqg"
)
```

At present, the **`SSQLite`** implementation solely supports the executescript function, which serves as a wrapper. This function is responsible for executing all queries specified in a single text file. Additionally, it generates an accompanying `.sqg` file with the designated name, alongside the existing `.db` file.

Moreover, to verify the expected functionality of the recovery function for predefined test cases, simply execute the test.py file.

``` bash
$ python3 test.py
```

Upon running the test code, if the result is returned as `OK`, it indicates that the generation of the undo query set has been successful as anticipated. Additionally, you can examine each test case along with its corresponding expected results directly within the `test.py` file.

---

## Data Structure(SQG)

`SSqliteQueryGraph` (SQG) is the central component of the **`SSqlite`** module which is a tree structure wherein each node represents an individual query statement. The structure of each node is implemented as the `SSqliteNode` class, located in the `ssqlite/node.py` file. The SSqliteNode class encompasses the following properties:

| Property | Required | Type | Description |
|---|---|---|---|
| `node_id` | True | `str` | Identifier of each node |
| `query_order` | True | `int` | Execution order of the query |
| `query_string` | True | `str` | The verbatim query string |
| `parent` | False | `str` | Reference to the parent node |
| `children` | False | `list[str]` | List of references to its child nodes |
| `primary_key` | False | `str` | The primary key (`rowid`) associated with the query |
| `target_table` | True | `str` | The table name associated with the query |
| `target_column` | False | `str` | The column name associated with the query |
| `flag_drop` | False | `bool` | Indicator whether the table has been dropped |
| `flag_delete` | False | `bool` | Indicator whether the row has been deleted |

Additional properties have been incorporated into the conventional tree node structures to facilitate the functioning of the revert mechanism. An example of such a property is `query_order`, which plays a vital role in the recovery algorithm by allowing efficient retrieval of the target node with a time complexity of $O(1)$. This property serves as a key within a hash map data structure referred to as the **Index**. Furthermore, properties like `primary_key` and `target_table` are utilized in the formulation of the undo query set through specifically designed algorithms.

The `Index` is an integral part of the `SSqliteQueryGraph`, serving as a hash map data structure designed to efficiently locate specific nodes using their corresponding keys. The inclusion of this additional component is crucial for optimizing the recovery algorithm's efficiency, as searching the entire tree structure would be time-consuming. By utilizing the `Index`, it becomes feasible to retrieve specific nodes based on their query order, as previously mentioned. Furthermore, it enables the search for specific nodes based on significant information such as the `primary_key` or `target_column`.

The combined functionality of the Index and the tree structure can be illustrated as follows:

![Overview](https://github.com/BluberryPie/ssqlite/assets/63835339/0115c204-ac09-41ae-8bb5-a2bbe60f89d4)

---

## Algorithm

---

## Statistics