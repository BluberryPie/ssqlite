import ssqlite.config

from pathlib import Path

from ssqlite.utils import NodeType, InvalidInstructionError
from ssqlite.utils import parse_inst_from_query_string
from ssqlite.node import SSqliteNode, CreateNode, InsertNode, UpdateNode, DropNode, DeleteNode


class SSqliteQueryGraph(object):
    
    def __init__(self):
        pass

    def add_node(self, node: SSqliteNode):
        pass

    def save_to_file(self, sqg_filename: str="ssqlite.sqg"):
        pass


def build_sqg_from_sql(sql_filename: str) -> None:
    """ Builds .sqg(ssqlite query graph) file from .sql file"""
    sqg = SSqliteQueryGraph()

    sql_filepath = Path(ssqlite.config.BASE_DIR) / "data" / sql_filename
    with open(sql_filepath, "r") as f:
        queries = f.readlines()
    
    for idx, query in enumerate(queries):
        try:
            inst = parse_inst_from_query_string(query)
        except InvalidInstructionError:
            continue
        
        if inst == NodeType.CREATE.name:
            node = CreateNode(query_order=idx + 1)
        elif inst == NodeType.INSERT.name:
            node = InsertNode(query_order=idx + 1)
        elif inst == NodeType.UPDATE.name:
            node = UpdateNode(query_order=idx + 1)
        elif inst == NodeType.DROP.name:
            node = DropNode(query_order=idx + 1)
        elif inst == NodeType.DELETE.name:
            node = DeleteNode(query_order=idx + 1)

        try:
            sqg.add_node(node)
        except Exception as e:
            pass

    sqg.save_to_file()
