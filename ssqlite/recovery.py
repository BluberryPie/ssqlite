from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.node import *


def generate_undo_query_create(node: CreateNode):
    pass


def generate_undo_query_insert(node: InsertNode):
    pass


def generate_undo_query_update(node: UpdateNode):
    pass


def generate_undo_query_drop(node: DropNode):
    pass


def generate_undo_query_delete(node: DeleteNode):
    pass


def generate_undo_query(graph: SQG, query_order: int) -> list[str]:
    """Generate undo query set"""
    undo_query_set = []
    target_node = graph.index.find_by_order(query_order=query_order)
    
    if isinstance(target_node, CreateNode):
        undo_query_set = generate_undo_query_create(target_node)
    elif isinstance(target_node, InsertNode):
        undo_query_set = generate_undo_query_insert(target_node)
    elif isinstance(target_node, UpdateNode):
        undo_query_set = generate_undo_query_update(target_node)
    elif isinstance(target_node, DropNode):
        undo_query_set = generate_undo_query_drop(target_node)
    elif isinstance(target_node, DeleteNode):
        undo_query_set = generate_undo_query_delete(target_node)

    return undo_query_set
