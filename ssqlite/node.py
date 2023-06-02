from abc import ABCMeta, abstractmethod


class SSqliteNode(metaclass=ABCMeta):

    node_id: int = 0

    def __init__(self, query_order: int): 
        self.node_id = str(SSqliteNode.node_id).rjust(5, "0")
        SSqliteNode.node_id += 1

        self.query_order: int = query_order

        self.parent: SSqliteNode = None
        self.children: list[SSqliteNode] = []

        self.primary_key: str = ""
        self.target_table: str = ""
        self.target_column: str = ""

        self.flag_delete: bool = False
        self.flag_drop: bool = False
    
    def __repr__(self):
        return f"SSqliteNode(node_id={self.node_id}, query_order={self.query_order})"

    def getParent(self):
        """Get parent node"""
        pass
    
    def getChild(self):
        """Get specific child"""
        pass

    @abstractmethod
    def setParent(self):
        """Set parent node"""
        pass

    @abstractmethod
    def addChild(self):
        """Add child node"""
        pass


class CreateNode(SSqliteNode):

    def __init__(self):
        super().__init__()
        pass

    def setParent(self):
        """Set parent node"""
        pass


class InsertNode(SSqliteNode):

    def __init__(self):
        super().__init__()
        pass

    def setParent(self):
        """Set parent node"""
        pass


class UpdateNode(SSqliteNode):

    def __init__(self):
        super().__init__()
        pass

    def setParent(self):
        """Set parent node"""
        pass


class DropNode(SSqliteNode):

    def __init__(self):
        super().__init__()
        pass

    def setParent(self):
        """Set parent node"""
        pass


class DeleteNode(SSqliteNode):

    def __init__(self):
        super().__init__()
        pass

    def setParent(self):
        """Set parent node"""
        pass
