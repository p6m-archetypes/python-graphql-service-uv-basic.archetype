"""
GraphQL API package for {{ PrefixName }}{{ SuffixName }}.

This package provides a complete GraphQL API implementation including:
- Schema definitions and types
- Query and mutation resolvers  
- Input type definitions
- GraphQL endpoint integration

The main entry point is the `schema` object which can be used with
FastAPI's GraphQL router or other GraphQL server implementations.
"""

from .schema import schema, Query, Mutation

__all__ = [
    "schema",
    "Query",
    "Mutation"
]
