"""
GraphQL implementation for {{ PrefixName }}{{ SuffixName }} server.

This package contains all GraphQL resolvers, monitoring, security,
and subscription implementations.
"""

from .schema import create_schema

__all__ = ["create_schema"] 