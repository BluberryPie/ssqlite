from enum import Enum


class NodeType(Enum):

    CREATE = 1
    INSERT = 2
    UPDATE = 3
    DROP = 4
    DELETE = 5


class InvalidInstructionError(Exception):

    def __init__(self, inst):
        self.msg =  f"[{inst}] is not DML or is not a valid instruction"

    def __str__(self):
        return self.msg


def parse_inst_from_query_string(query_string: str) -> NodeType:
    """ Parse instruction from query string"""
    inst = query_string.split()[0]
    if inst not in [nt.name for nt in NodeType]:
        raise InvalidInstructionError(inst)

    return inst
