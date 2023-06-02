import pickle
import sqlite3
import ssqlite.config

from pathlib import Path

from ssqlite.index import Index
from ssqlite.utils import NodeType, InvalidInstructionError
from ssqlite.utils import parse_query_string
from ssqlite.node import SSqliteNode, CreateNode, InsertNode, UpdateNode, DropNode, DeleteNode


class SSqliteQueryGraph(object):
    
    def __init__(self):
        self.index: Index = Index()

    def add_node(self, node: SSqliteNode):
        print(f"Adding {node}")
        if isinstance(node, CreateNode):
            # Add create node to index
            self.index.add(node)
        elif isinstance(node, InsertNode):
            # 1. Add insert node to index
            self.index.add(node)
            # 2. Find its corresponding CreateNode from the index(using table name)
            parent_create_node = self.index.find(_from="create", _key=node.target_table)
            # 3. Set the CreateNode as its parent
            node.set_parent(parent_create_node)
            # 4. Add child to CreateNode
            parent_create_node.add_child(node)
        elif isinstance(node, UpdateNode):
            # 1. Add update node to index
            # 2. Find its corresponding InsertNode or UpdateNode from the index
            # 3. Set the InsertNode or UpdateNode as its parent
            # 4. Add child to InsertNode or UpdateNode
            pass
        elif isinstance(node, DropNode):
            # 1. Add drop node to index
            self.index.add(node)
            # 2. Find its corresponding CreateNode from the index(using table name)
            parent_create_node = self.index.find(_from="create", _key=node.target_table)
            # 3. Set the CreateNode as its parent
            node.set_parent(parent_create_node)
            # 4. Set flag_drop=True in parent CreateNode
            parent_create_node.set_drop_flag()
            # 5. Add child to CreateNode
            parent_create_node.add_child(node)
        elif isinstance(node, DeleteNode):
            # 1. Add delete node to index
            self.index.add(node)
            # 2. Find it corresponding InsertNode from the index(using table name and primary key)
            # 3. Set the InsertNode as its parent
            # 4. Set flag_delete=True in parent InsertNode
            # 5. Add child to InsertNode
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
            parsed_query = parse_query_string(query)
            # Explode
            inst = parsed_query["inst"]
            table_name = parsed_query["table_name"]
            column_name = parsed_query["column_name"]
            condition = parsed_query["condition"]
        except InvalidInstructionError:
            continue
        
        if inst == NodeType.CREATE.name:
            cursor.execute(query)
            node = CreateNode(
                query_order=idx + 1,
                target_table=table_name
            )
        elif inst == NodeType.INSERT.name:
            cursor.execute(query)
            insert_pk = cursor.lastrowid
            node = InsertNode(
                query_order=idx + 1,
                primary_key=insert_pk,
                target_table=table_name
            )
        elif inst == NodeType.UPDATE.name:
            # Add preliminary query to get primary key
            cursor.execute(f"SELECT FROM {table_name} {condition}")
            update_pk = cursor.lastrowid
            # Execute actual query
            cursor.execute(query)
            node = UpdateNode(
                query_order=idx + 1,
                primary_key=update_pk,
                target_table=table_name,
                target_column=column_name
            )
        elif inst == NodeType.DROP.name:
            node = DropNode(
                query_order=idx + 1,
                target_table=table_name
            )
        elif inst == NodeType.DELETE.name:
            # Add preliminary query to get primary key
            cursor.execute(f"SELECT FROM {table_name} {condition}")
            delete_pk = cursor.lastrowid
            # Execute actual query
            cursor.execute(query)
            node = DeleteNode(
                query_order=idx + 1,
                primary_key=delete_pk,
                target_table=table_name
            )

        try:
            sqg.add_node(node)
        except Exception as e:
            pass

    SSqliteQueryGraph.save_to_file(sqg)
