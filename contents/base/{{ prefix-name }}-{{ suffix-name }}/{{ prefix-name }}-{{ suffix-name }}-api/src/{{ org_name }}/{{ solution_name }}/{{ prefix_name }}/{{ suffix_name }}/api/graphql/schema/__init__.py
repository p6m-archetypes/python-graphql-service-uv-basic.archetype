"""
GraphQL schema package for {{ PrefixName }}{{ SuffixName }}.

This package contains all GraphQL schema definitions, types, and schema registry
functionality for the {{ PrefixName }}{{ SuffixName }} service.
"""

from .base import schema, Query, Mutation

__all__ = [
    "schema",
    "Query", 
    "Mutation"
]
