from ssqlite.algo import SSqliteQueryGraph as SQG
from ssqlite.node import *


def generate_undo_query_create(graph: SQG, node: CreateNode):
    pass


def generate_undo_query_insert(graph: SQG, node: InsertNode):
    pass


def generate_undo_query_update(graph: SQG, node: UpdateNode):
    pass


def generate_undo_query_drop(graph: SQG, node: DropNode):
    pass


def generate_undo_query_delete(graph: SQG, node: DeleteNode):
    # 1. Find corresponding InsertNode(=parent)
    insert_node = node.get_parent()
    # 2. Find all following updates
    update_nodes = []
    updated_columns = insert_node.get_all_updated_columns()
    for column in updated_columns:
        last_update = graph.index.find_last_update(
            table_name=node.target_table,
            primary_key=node.primary_key,
            column_name=column
        )
        update_nodes.append(last_update)
    
    undo_query_set = [insert_node.query_string] + [update_node.query_string for update_node in update_nodes]
    return undo_query_set


def generate_undo_query(graph: SQG, query_order: int) -> list[str]:
    """Generate undo query set"""
    undo_query_set = []
    target_node = graph.index.find_by_order(query_order=query_order)
    
    if isinstance(target_node, CreateNode):
        undo_query_set = generate_undo_query_create(graph, target_node)
    elif isinstance(target_node, InsertNode):
        undo_query_set = generate_undo_query_insert(graph, target_node)
    elif isinstance(target_node, UpdateNode):
        undo_query_set = generate_undo_query_update(graph, target_node)
    elif isinstance(target_node, DropNode):
        undo_query_set = generate_undo_query_drop(graph, target_node)
    elif isinstance(target_node, DeleteNode):
        undo_query_set = generate_undo_query_delete(graph, target_node)

    return undo_query_set
