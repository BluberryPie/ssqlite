import pickle
import sqlite3
import ssqlite.config

from pathlib import Path

from ssqlite.utils import NodeType, InvalidInstructionError
from ssqlite.utils import parse_query_string
from ssqlite.node import SSqliteNode, CreateNode, InsertNode, UpdateNode, DropNode, DeleteNode


class SSqliteQueryGraph(object):
    
    def __init__(self):
        self.data: list[SSqliteNode] = []

    def add_node(self, node: SSqliteNode):
        print(f"Adding {node}")
        if isinstance(node, CreateNode):
            self.data.append(node)
        elif isinstance(node, InsertNode):
            pass
        elif isinstance(node, UpdateNode):
            pass
        elif isinstance(node, DropNode):
            pass
        elif isinstance(node, DeleteNode):
            pass

    @classmethod
    def load_from_file(self, sqg_filename: str="ssqlite.sqg"):
        """Load SQG from pickled file"""
        sqg_filepath = Path(ssqlite.config.BASE_DIR) / sqg_filename
        with open(sqg_filepath, "rb") as f:
            graph = pickle.load(f)
        return graph

    @classmethod
    def save_to_file(self, graph, sqg_filename: str="ssqlite.sqg") -> None:
        """Save SQG object using pickle"""
        sqg_filepath = Path(ssqlite.config.BASE_DIR) / sqg_filename
        with open(sqg_filepath, "wb") as f:
            pickle.dump(graph, f, pickle.HIGHEST_PROTOCOL)


def build_sqg_from_sql(cursor: sqlite3.Cursor, sql_filename: str) -> None:
    """ Builds .sqg(ssqlite query graph) file from .sql file"""
    sqg = SSqliteQueryGraph()

    sql_filepath = Path(ssqlite.config.BASE_DIR) / "data" / sql_filename
    with open(sql_filepath, "r") as f:
        queries = f.readlines()
    
    for idx, query in enumerate(queries):
        try:
            cursor.execute(query)
        except sqlite3.OperationalError as e:
            print(f"Something wrong with the query...\n{e}")
        else:
            primary_key = cursor.lastrowid

        try:
            parsed_query = parse_query_string(query)
            inst = parsed_query["inst"]
            table_name = parsed_query["table_name"]
            column_name = parsed_query["column_name"]

        except InvalidInstructionError:
            continue
        
        if inst == NodeType.CREATE.name:
            node = CreateNode(query_order=idx + 1, target_table=table_name)
        elif inst == NodeType.INSERT.name:
            node = InsertNode(query_order=idx + 1, primary_key=primary_key, target_table=table_name)
        elif inst == NodeType.UPDATE.name:
            node = UpdateNode(query_order=idx + 1, target_table=table_name, target_column=column_name)
        elif inst == NodeType.DROP.name:
            node = DropNode(query_order=idx + 1, target_table=table_name)
        elif inst == NodeType.DELETE.name:
            node = DeleteNode(query_order=idx + 1, target_table=table_name)

        try:
            sqg.add_node(node)
        except Exception as e:
            pass

    SSqliteQueryGraph.save_to_file(sqg)
