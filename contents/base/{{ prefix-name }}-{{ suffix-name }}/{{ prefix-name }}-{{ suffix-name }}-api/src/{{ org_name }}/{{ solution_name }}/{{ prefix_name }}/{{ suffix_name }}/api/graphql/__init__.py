"""
GraphQL API package for {{ PrefixName }}{{ SuffixName }}.

This package contains pure GraphQL schema definitions including types,
inputs, and base schema structure without any resolver implementations.
All resolvers are implemented in the server package.
"""

from .schema.base import create_pure_schema

__all__ = ["create_pure_schema"]
