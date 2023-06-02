from abc import ABCMeta, abstractmethod

from ssqlite.utils import NodeType


class OrphanError(Exception):

    def __init__(self, node_id):
        self.msg = f"SSqliteNode<{node_id}> has no parent"
    
    def __str__(self):
        return self.msg


class SSqliteNode(metaclass=ABCMeta):

    node_id: int = 0

    def __init__(self, query_order: int, primary_key: str="", target_table: str="", target_column: str=""):
        self.node_id = str(SSqliteNode.node_id).rjust(5, "0")
        SSqliteNode.node_id += 1

        self.query_order: int = query_order

        self.parent: SSqliteNode = None
        self.children: list[SSqliteNode] = []

        self.primary_key: str = primary_key
        self.target_table: str = target_table
        self.target_column: str = target_column

        self.flag_delete: bool = False
        self.flag_drop: bool = False
    
    def __repr__(self):
        return f"SSqliteNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_parent(self):
        """Get parent node"""
        parent_node = self.parent
        if parent_node is None:
            raise OrphanError(self.node_id)
        return parent_node
    
    @abstractmethod
    def get_child(self, node_type: NodeType):
        """Get specific child"""
        pass

    @abstractmethod
    def set_parent(self):
        """Set parent node"""
        pass

    @abstractmethod
    def add_child(self):
        """Add child node"""
        pass


class CreateNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def get_child(self, node_type):
        """Get specific child"""
        pass

    def set_parent(self):
        """Set parent node"""
        pass

    def add_child(self):
        """Add child node"""
        pass


class InsertNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def get_child(self, node_type):
        """Get specific child"""
        pass

    def set_parent(self):
        """Set parent node"""
        pass

    def add_child(self):
        """Add child node"""
        pass


class UpdateNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def set_parent(self):
        """Set parent node"""
        pass

    def add_child(self):
        """Add child node"""
        pass


class DropNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def set_parent(self):
        """Set parent node"""
        pass

    def add_child(self):
        """Add child node"""
        pass


class DeleteNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def set_parent(self):
        """Set parent node"""
        pass

    def add_child(self):
        """Add child node"""
        pass
