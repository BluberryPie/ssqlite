from collections import defaultdict

from ssqlite.node import SSqliteNode, CreateNode, InsertNode, UpdateNode, DropNode, DeleteNode


class NodeNotFound(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class Index(object):
    
    def __init__(self):
        self.order_index = {}
        self.create_index = {}
        self.insert_index = {}
        self.update_index = defaultdict(list)
        self.drop_index = {}
        self.delete_index = {}
    
    def add(self, node: SSqliteNode) -> None:
        """Add node to index"""
        if isinstance(node, CreateNode):
            self.create_index[node.target_table] = node
        elif isinstance(node, InsertNode):
            self.insert_index[f"{node.target_table}-{node.primary_key}"] = node
        elif isinstance(node, UpdateNode):
            self.update_index[f"{node.target_table}-{node.primary_key}-{node.target_column}"].append(node)
        elif isinstance(node, DropNode):
            self.drop_index[node.target_table] = node
        elif isinstance(node, DeleteNode):
            self.delete_index[f"{node.target_table}-{node.primary_key}"] =  node
        # Add another mapping for O(1) search at recovery
        self.order_index[node.query_order] = node

    def find(self, _from: str, _key: str) -> SSqliteNode:
        """Find specific node from index"""
        try:
            node = getattr(self, f"{_from.lower()}_index")[_key]
        except Exception:
            raise NodeNotFound(f"{_from.lower()} node with key: [{_key}] doesn't exist")
        return node
    
    def find_by_order(self, query_order: int) -> SSqliteNode:
        """Find specific node based on query order"""
        node = self.order_index.get(query_order, None)
        if node is None:
            raise NodeNotFound(f"Node with query order [{query_order}] doesn't exist")
        return node
    
    def find_last_update(self, table_name: str, primary_key: str, column_name: str) -> UpdateNode:
        """Find last update node based on given _key"""
        try:
            last_update_node = self.update_index[f"{table_name}-{primary_key}-{column_name}"][-1]
        except Exception:
            return None
        return last_update_node