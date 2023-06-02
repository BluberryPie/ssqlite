from collections import defaultdict

from ssqlite.node import SSqliteNode, CreateNode, InsertNode, UpdateNode, DropNode, DeleteNode


class NodeNotFound(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class Index(object):
    
    def __init__(self):
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
            self.update_index[f"{node.target_table}-{node.target_column}"].append(node)
        elif isinstance(node, DropNode):
            self.drop_index[node.target_table] = node
        elif isinstance(node, DeleteNode):
            self.delete_index[f"{node.target_table}-{node.primary_key}"] =  node

    def find(self, _from: str, _key: str) -> SSqliteNode:
        """Find specific node from index"""
        try:
            node = getattr(self, f"{_from.lower()}_index")[_key]
        except Exception:
            raise NodeNotFound(f"{_from.lower()} node with key: [{_key}] doesn't exist")

        return node
