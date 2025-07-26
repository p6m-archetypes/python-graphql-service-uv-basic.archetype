"""
GraphQL input types for {{ PrefixName }}{{ SuffixName }}.

This package contains Strawberry input types for mutations, queries, and filtering.
These inputs provide the GraphQL API interface for creating, updating, and querying
{{ prefix_name }} entities.
"""

from .mutations import Create{{ PrefixName }}Input, Update{{ PrefixName }}Input
from .queries import {{ PrefixName }}Filter, {{ PrefixName }}Sort, SortDirection

__all__ = [
    "Create{{ PrefixName }}Input",
    "Update{{ PrefixName }}Input",
    "{{ PrefixName }}Filter",
    "{{ PrefixName }}Sort", 
    "SortDirection"
]
