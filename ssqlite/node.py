from abc import ABCMeta, abstractmethod


class OrphanError(Exception):

    def __init__(self, node_id):
        self.msg = f"SSqliteNode<{node_id}> has no parent"
    
    def __str__(self):
        return self.msg


class InvalidOperation(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class InvalidParent(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class InvalidChild(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class SSqliteNode(metaclass=ABCMeta):

    node_id: int = 0

    def __init__(
            self, query_order: int, query_string: str,
            primary_key: str="", target_table: str="", target_column: str=""
        ):
        self.node_id = str(SSqliteNode.node_id).rjust(5, "0")
        SSqliteNode.node_id += 1

        self.query_order: int = query_order
        self.query_string: str = query_string

        self.parent: SSqliteNode = None
        self.children: list[SSqliteNode] = []

        self.primary_key: str = primary_key
        self.target_table: str = target_table
        self.target_column: str = target_column
    
    def __repr__(self):
        return f"SSqliteNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_parent(self):
        """Get parent node"""
        parent_node = self.parent
        if parent_node is None:
            raise OrphanError(self.node_id)
        return parent_node
    
    @abstractmethod
    def get_child(self):
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
        self.flag_drop: bool = False

    def __repr__(self):
        return f"CreateNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_child(self):
        """Get specific child"""
        pass

    def set_parent(self):
        """Set parent node"""
        raise InvalidOperation("CreateNode cannot have a parent node")

    def add_child(self, node: SSqliteNode):
        """Add child node"""
        if isinstance(node, InsertNode) or isinstance(node, DropNode):
            self.children.append(node)
        else:
            raise InvalidChild(f"[{type(node)}] cannot be a child of CreateNode")
    
    def set_drop_flag(self):
        """Set flag_drop to True"""
        self.flag_drop = True


class InsertNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flag_delete: bool = False

    def __repr__(self):
        return f"InsertNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_child(self):
        """Get specific child"""
        pass

    def set_parent(self, node: CreateNode):
        """Set parent node"""
        if isinstance(node, CreateNode):
            self.parent = node
        else:
            raise InvalidParent(f"[{type(node)}] cannot be a parent of InsertNode")

    def add_child(self, node: SSqliteNode):
        """Add child node"""
        if isinstance(node, UpdateNode) or isinstance(node, DeleteNode):
            self.children.append(node)
        else:
            raise InvalidChild(f"[{type(node)}] cannot be a child of InsertNode")

    def set_delete_flag(self):
        """Set flag_delete to True"""
        self.flag_delete=True
    
    def get_all_updated_columns(self):
        """Return all updated columnd"""
        updated_columns = set()
        
        for child in self.children:
            if isinstance(child, UpdateNode):
                updated_columns.add(child.target_column)
        
        return updated_columns


class UpdateNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def __repr__(self):
        return f"UpdateNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_child(self):
        """Get specific child"""
        pass

    def set_parent(self, node: SSqliteNode):
        """Set parent node"""
        if isinstance(node, InsertNode) or isinstance(node, UpdateNode):
            self.parent = node
        else:
            raise InvalidParent(f"[{type(node)}] cannot be a parent of UpdateNode")

    def add_child(self, node: SSqliteNode):
        """Add child node"""
        if isinstance(node, UpdateNode):
            if self.children:
                raise InvalidChild("UpdateNode can have only 1 child maximum")
            self.children.append(node)
        else:
            raise InvalidChild(f"[{type(node)}] cannot be a child of UpdateNode")


class DropNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def __repr__(self):
        return f"DropNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_child(self):
        """Get specific child"""
        pass

    def set_parent(self, node: CreateNode):
        """Set parent node"""
        if isinstance(node, CreateNode):
            self.parent = node
        else:
            raise InvalidParent(f"[{type(node)}] cannot be a parent of DropNode")

    def add_child(self, node: CreateNode):
        """Add child node"""
        raise InvalidOperation("DropNode cannot have a child node")


class DeleteNode(SSqliteNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def __repr__(self):
        return f"DeleteNode(node_id={self.node_id}, query_order={self.query_order})"

    def get_child(self):
        """Get specific child"""
        pass

    def set_parent(self, node: InsertNode):
        """Set parent node"""
        if isinstance(node, InsertNode):
            self.parent = node
        else:
            raise InvalidParent(f"[{type(node)}] cannot be a parent of DeleteNode")

    def add_child(self, node: InsertNode):
        """Add child node"""
        raise InvalidOperation("DeleteNode cannot have a child node")
