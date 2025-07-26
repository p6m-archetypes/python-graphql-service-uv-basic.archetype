"""
GraphQL resolvers package for {{ PrefixName }}{{ SuffixName }}.

This package contains all GraphQL resolver functions that handle queries, mutations,
and field resolution. Resolvers connect the GraphQL schema to the business logic
and data access layers.
"""

from .query_resolvers import {{ PrefixName }}QueryResolver
from .mutation_resolvers import {{ PrefixName }}MutationResolver
from .dataloader import {{ PrefixName }}DataLoader, create_dataloaders
from .context import ResolverContext

__all__ = [
    "{{ PrefixName }}QueryResolver",
    "{{ PrefixName }}MutationResolver",
    "{{ PrefixName }}DataLoader", 
    "create_dataloaders",
    "ResolverContext"
]
