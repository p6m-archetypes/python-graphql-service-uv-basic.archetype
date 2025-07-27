"""
Pure GraphQL schema definitions for {{ PrefixName }}{{ SuffixName }}.

This module contains only the GraphQL schema structure including
the root Query, Mutation, and Subscription type definitions without
any resolver implementations. Resolvers are implemented in the server package.
"""

import strawberry
from typing import Optional, List

# Import GraphQL types
from .types import (
    {{ PrefixName }}Type,
    {{ PrefixName }}Connection,
    {{ PrefixName }}ConnectionArgs,
    {{ PrefixName }}Response,
    Delete{{ PrefixName }}Response
)

# Import input types  
from ..inputs import (
    {{ PrefixName }}Filter,
    {{ PrefixName }}Sort,
    Create{{ PrefixName }}Input,
    Update{{ PrefixName }}Input,
    CreateMultiple{{ PrefixName }}Input
)


@strawberry.type
class Query:
    """
    Root GraphQL Query type.
    
    This is a pure schema definition without resolver implementations.
    All resolvers are implemented in the server package.
    """
    
    # Placeholder field to make the schema valid
    # Actual resolvers are implemented in the server package
    _schema_info: str = strawberry.field(description="Schema information - resolvers implemented in server package")


@strawberry.type  
class Mutation:
    """
    Root GraphQL Mutation type.
    
    This is a pure schema definition without resolver implementations.
    All resolvers are implemented in the server package.
    """
    
    # Placeholder field to make the schema valid
    # Actual resolvers are implemented in the server package
    _schema_info: str = strawberry.field(description="Schema information - resolvers implemented in server package")


@strawberry.type
class Subscription:
    """
    Root GraphQL Subscription type.
    
    This is a pure schema definition without resolver implementations.
    All resolvers are implemented in the server package.
    """
    
    # Placeholder field to make the schema valid
    # Actual resolvers are implemented in the server package
    _schema_info: str = strawberry.field(description="Schema information - resolvers implemented in server package")


def create_pure_schema() -> strawberry.Schema:
    """
    Create a pure GraphQL schema with type definitions only.
    
    This schema contains no resolver implementations or extensions.
    It's designed to be extended by the server package with actual resolvers.
    
    Returns:
        strawberry.Schema: Pure schema with type definitions
    """
    return strawberry.Schema(
        query=Query,
        mutation=Mutation, 
        subscription=Subscription,
        # No extensions or resolvers - pure schema only
    ) 