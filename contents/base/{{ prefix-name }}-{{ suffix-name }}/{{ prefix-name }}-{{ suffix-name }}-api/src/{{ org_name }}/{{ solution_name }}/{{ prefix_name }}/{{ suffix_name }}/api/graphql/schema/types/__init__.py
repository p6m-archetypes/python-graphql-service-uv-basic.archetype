"""
GraphQL types package for {{ PrefixName }}{{ SuffixName }}.

This package contains all Strawberry GraphQL types including entities,
connections for pagination, and utility functions for converting between
Pydantic models and GraphQL types.
"""

# Entity types
from .entities import (
    {{ PrefixName }}Type,
    {{ PrefixName }}Response,
    Delete{{ PrefixName }}Response,
    example_dto_to_graphql,
    graphql_to_example_dto
)

# Connection types for pagination
from .connections import (
    PageInfo,
    {{ PrefixName }}Edge,
    {{ PrefixName }}Connection,
    {{ PrefixName }}ConnectionArgs,
    encode_cursor,
    decode_cursor,
    page_result_to_connection,
    create_empty_connection
)

# Utility functions
from .utils import (
    convert_pydantic_field_type,
    extract_field_info,
    pydantic_to_strawberry_type,
    create_strawberry_from_pydantic,
    create_pydantic_from_strawberry
)

__all__ = [
    # Entity types
    "{{ PrefixName }}Type",
    "{{ PrefixName }}Response", 
    "Delete{{ PrefixName }}Response",
    "example_dto_to_graphql",
    "graphql_to_example_dto",
    
    # Connection types
    "PageInfo",
    "{{ PrefixName }}Edge",
    "{{ PrefixName }}Connection",
    "{{ PrefixName }}ConnectionArgs",
    "encode_cursor",
    "decode_cursor",
    "page_result_to_connection",
    "create_empty_connection",
    
    # Utility functions
    "convert_pydantic_field_type",
    "extract_field_info", 
    "pydantic_to_strawberry_type",
    "create_strawberry_from_pydantic",
    "create_pydantic_from_strawberry"
]
