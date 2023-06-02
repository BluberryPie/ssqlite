import re

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


def parse_table_name(pattern: str, query_string: str) -> str:
    """Helper function for parsing table name from query string"""
    table_name_match = re.search(pattern=pattern, string=query_string, flags=re.IGNORECASE)
    try:
        table_name = table_name_match.group("table_name")
    except AttributeError:
        raise

    return table_name


def parse_column_name(pattern: str, query_string: str) -> str:
    """Helper function for parsing column name from query string"""
    column_name_match = re.search(pattern=pattern, string=query_string, flags=re.IGNORECASE)
    try:
        column_name = column_name_match.group("column_name")
    except AttributeError:
        raise

    return column_name


def parse_condition(pattern: str, query_string: str) -> str:
    """Helper function for parsing condition caluse in query string"""
    where_clause_match = re.search(pattern=pattern, string=query_string, flags=re.IGNORECASE)
    try:
        condition = where_clause_match.group("condition")
    except AttributeError:
        raise

    return condition


def parse_query_string(query_string: str) -> dict:
    """Parse query string"""
    inst = query_string.split()[0]
    if inst not in [nt.name for nt in NodeType]:
        raise InvalidInstructionError(inst)

    table_name = None
    column_name = None
    condition = None

    if inst == NodeType.CREATE.name:
        table_name = parse_table_name(
            pattern=r"TABLE(\s+)(?P<table_name>[a-zA-Z0-9_]+)(\s+)",
            query_string=query_string
        )
    elif inst == NodeType.INSERT.name:
        table_name = parse_table_name(
            pattern=r"INSERT(\s+)INTO(\s+)(?P<table_name>[a-zA-Z0-9_]+)",
            query_string=query_string
        )
    elif inst == NodeType.UPDATE.name:
        table_name = parse_table_name(
            pattern=r"UPDATE(\s+)(?P<table_name>[a-zA-Z0-9_]+)(\s+)SET",
            query_string=query_string
        )
        column_name = parse_column_name(
            pattern=r"SET(\s+)(?P<column_name>[a-zA-Z0-9_]+)(\s*)=",
            query_string=query_string
        )
        condition = parse_condition(
            pattern=r"(?P<condition>WHERE(\s+)([a-zA-Z0-9_]*)(\s*)=(\s*)(\'?)(\"?)([a-zA-Z0-9_]+)(\'?)(\"?))",
            query_string=query_string
        )
    elif inst == NodeType.DROP.name:
        table_name = parse_table_name(
            pattern=r"DROP(\s+)TABLE(\s+)(?P<table_name>[a-zA-Z0-9_]+)",
            query_string=query_string
        )
    elif inst == NodeType.DELETE.name:
        table_name = parse_table_name(
            pattern=r"DELETE(\s+)FROM(\s+)(?P<table_name>[a-zA-Z0-9_]+)(\s+)",
            query_string=query_string
        )
        condition = parse_condition(
            pattern=r"(?P<condition>WHERE(\s+)([a-zA-Z0-9_]*)(\s*)=(\s*)(\'?)(\"?)([a-zA-Z0-9_]+)(\'?)(\"?))",
            query_string=query_string
        )

    result = {
        "inst": inst,
        "table_name": table_name,
        "column_name": column_name,
        "condition": condition
    }

    return result
