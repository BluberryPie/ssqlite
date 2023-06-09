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
        if isinstance(node, CreateNode):
            # Add create node to index
            self.index.add(node)
        elif isinstance(node, InsertNode):
            # 1. Find its corresponding CreateNode from the index(using table name)
            parent_create_node = self.index.find(
                _from="create",
                _key=node.target_table
            )
            # 2. Set the CreateNode as its parent
            node.set_parent(parent_create_node)
            # 3. Add child to CreateNode
            parent_create_node.add_child(node)
            # 4. Add insert node to index
            self.index.add(node)
        elif isinstance(node, UpdateNode):
            # 1. Find its corresponding InsertNode or UpdateNode from the index
            corr_insert_node = self.index.find(
                _from="insert",
                _key=f"{node.target_table}-{node.primary_key}"
            )
            last_update_node = self.index.find_last_update(
                table_name=node.target_table,
                primary_key=node.primary_key,
                column_name=node.target_column
            )
            parent_node = corr_insert_node if last_update_node is None else last_update_node
            # 2. Set the InsertNode or UpdateNode as its parent
            node.set_parent(parent_node)
            # 3. Add child to InsertNode or UpdateNode
            parent_node.add_child(node)
            # 4. Add update node to index
            self.index.add(node)
        elif isinstance(node, DropNode):
            # 1. Find its corresponding CreateNode from the index(using table name)
            parent_create_node = self.index.find(_from="create", _key=node.target_table)
            # 2. Set the CreateNode as its parent
            node.set_parent(parent_create_node)
            # 3. Set flag_drop=True in parent CreateNode
            parent_create_node.set_drop_flag()
            # 4. Add child to CreateNode
            parent_create_node.add_child(node)
            # 5. Add drop node to index
            self.index.add(node)
        elif isinstance(node, DeleteNode):
            # 1. Find it corresponding InsertNode from the index(using table name and primary key)
            parent_insert_node = self.index.find(_from="insert", _key=f"{node.target_table}-{node.primary_key}")
            # 2. Set the InsertNode as its parent
            node.set_parent(parent_insert_node)
            # 3. Set flag_delete=True in parent InsertNode
            parent_insert_node.set_delete_flag()
            # 4. Add child to InsertNode
            parent_insert_node.add_child(node)
            # 5. Add delete node to index
            self.index.add(node)

    @classmethod
    def load_from_file(cls, sqg_filename: str="ssqlite.sqg"):
        """Load SQG from pickled file"""
        sqg_filepath = Path(ssqlite.config.BASE_DIR) / sqg_filename
        with open(sqg_filepath, "rb") as f:
            graph = pickle.load(f)
        return graph

    @classmethod
    def save_to_file(cls, graph, sqg_filename: str="ssqlite.sqg") -> None:
        """Save SQG object using pickle"""
        sqg_filepath = Path(ssqlite.config.BASE_DIR) / sqg_filename
        with open(sqg_filepath, "wb") as f:
            pickle.dump(graph, f, pickle.HIGHEST_PROTOCOL)


def build_sqg_from_sql(cursor: sqlite3.Cursor, sql_filename: str, sqg_filename: str) -> None:
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
                query_string=query.strip(),
                target_table=table_name
            )
        elif inst == NodeType.INSERT.name:
            cursor.execute(query)
            insert_pk = cursor.lastrowid
            node = InsertNode(
                query_order=idx + 1,
                query_string=query.strip(),
                primary_key=insert_pk,
                target_table=table_name
            )
        elif inst == NodeType.UPDATE.name:
            # Add preliminary query to get primary key
            cursor.execute(f"SELECT rowid FROM {table_name} {condition}")
            update_pk = cursor.fetchone()[0]
            # Execute actual query
            cursor.execute(query)
            node = UpdateNode(
                query_order=idx + 1,
                query_string=query.strip(),
                primary_key=update_pk,
                target_table=table_name,
                target_column=column_name
            )
        elif inst == NodeType.DROP.name:
            node = DropNode(
                query_order=idx + 1,
                query_string=query.strip(),
                target_table=table_name
            )
        elif inst == NodeType.DELETE.name:
            # Add preliminary query to get primary key
            cursor.execute(f"SELECT rowid FROM {table_name} {condition}")
            delete_pk = cursor.fetchone()[0]
            # Execute actual query
            cursor.execute(query)
            node = DeleteNode(
                query_order=idx + 1,
                query_string=query.strip(),
                primary_key=delete_pk,
                target_table=table_name
            )

        try:
            sqg.add_node(node)
        except Exception as e:
            pass

    SSqliteQueryGraph.save_to_file(graph=sqg, sqg_filename=sqg_filename)
