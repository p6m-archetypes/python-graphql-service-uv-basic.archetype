"""
Complete GraphQL schema definitions for {{ PrefixName }}{{ SuffixName }}.

This module contains the complete GraphQL schema structure including
the root Query, Mutation, and Subscription types with all resolvers integrated
for a full-featured real-time GraphQL API.
"""

import strawberry
from typing import Optional, List, AsyncGenerator

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

# Import subscription types
from ..subscriptions.types import (
    {{ PrefixName }}ChangeEvent,
    SubscriptionFilter,
    SubscriptionStats
)

# Import resolvers
from ..resolvers.query_resolvers import {{ PrefixName }}QueryResolver
from ..resolvers.mutation_resolvers import {{ PrefixName }}MutationResolver
from ..subscriptions.subscription_resolvers import {{ PrefixName }}SubscriptionResolver


@strawberry.type
class Query:
    """
    The root query type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.

    This contains all available query operations that clients can perform
    to retrieve data from the service. All queries are efficiently handled
    with DataLoader caching and proper pagination support.
    """

    @strawberry.field
    def health(self) -> str:
        """
        Health check for the GraphQL service.
        Returns a simple status string indicating the service is operational.
        """
        return "GraphQL service is healthy"

    @strawberry.field
    def version(self) -> str:
        """
        Returns the current version of the GraphQL API.
        """
        return "1.0.0"

    # {{ PrefixName }} queries
    {{ prefix_name }}: Optional[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.{{ prefix_name }},
        description="Get a single {{ prefix_name }} by ID"
    )

    {{ prefix_name }}_by_name: Optional[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.{{ prefix_name }}_by_name,
        description="Get a {{ prefix_name }} by name"
    )

    {{ prefix_name }}s: {{ PrefixName }}Connection = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.{{ prefix_name }}s,
        description="Get a paginated list of {{ prefix_name }}s with filtering and sorting"
    )

    search_{{ prefix_name }}s: List[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.search_{{ prefix_name }}s,
        description="Search {{ prefix_name }}s by name pattern"
    )

    {{ prefix_name }}s_by_status: List[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.{{ prefix_name }}s_by_status,
        description="Get {{ prefix_name }}s filtered by status"
    )

    recent_{{ prefix_name }}s: List[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.recent_{{ prefix_name }}s,
        description="Get recently created {{ prefix_name }}s"
    )

    {{ prefix_name }}_stats: strawberry.scalars.JSON = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.{{ prefix_name }}_stats,
        description="Get {{ prefix_name }} statistics by status"
    )


@strawberry.type
class Mutation:
    """
    The root mutation type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.

    This contains all available mutation operations that clients can perform
    to modify data in the service. All mutations include comprehensive validation,
    error handling, transaction support, and real-time event broadcasting.
    """

    @strawberry.mutation
    def ping(self) -> str:
        """
        A simple ping mutation to test connectivity and mutation functionality.
        Returns 'pong' if successful.
        """
        return "pong"

    # {{ PrefixName }} mutations
    create_{{ prefix_name }}: {{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.create_{{ prefix_name }},
        description="Create a new {{ prefix_name }} with validation and business rules"
    )

    update_{{ prefix_name }}: {{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.update_{{ prefix_name }},
        description="Update an existing {{ prefix_name }} with validation and conflict checking"
    )

    delete_{{ prefix_name }}: Delete{{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.delete_{{ prefix_name }},
        description="Delete a {{ prefix_name }} with confirmation and business rule validation"
    )

    create_multiple_{{ prefix_name }}s: List[{{ PrefixName }}Response] = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.create_multiple_{{ prefix_name }}s,
        description="Create multiple {{ prefix_name }}s in a single batch operation"
    )


@strawberry.type
class Subscription:
    """
    The root subscription type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.

    This contains all available subscription operations that clients can use
    to receive real-time updates about {{ prefix_name }} changes through WebSocket
    connections. All subscriptions support filtering and authorization.
    """

    # {{ PrefixName }} subscriptions
    {{ prefix_name }}_changes: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.{{ prefix_name }}_changes,
        description="Subscribe to all {{ prefix_name }} changes (create, update, delete, status changes)"
    )

    {{ prefix_name }}_created: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.{{ prefix_name }}_created,
        description="Subscribe specifically to {{ prefix_name }} creation events"
    )

    {{ prefix_name }}_updated: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.{{ prefix_name }}_updated,
        description="Subscribe to {{ prefix_name }} update events with optional entity-specific filtering"
    )

    {{ prefix_name }}_deleted: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.{{ prefix_name }}_deleted,
        description="Subscribe to {{ prefix_name }} deletion events"
    )

    {{ prefix_name }}_batch_operations: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.{{ prefix_name }}_batch_operations,
        description="Subscribe to batch operation events for multiple {{ prefix_name }}s"
    )

    subscription_stats: AsyncGenerator[SubscriptionStats, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscription_stats,
        description="Subscribe to real-time statistics about the subscription system (admin only)"
    )


# Create the complete schema with query, mutation, and subscription types
schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation,
    subscription=Subscription,
    description="{{ PrefixName }}{{ SuffixName }} GraphQL API - A modern real-time GraphQL service with comprehensive querying, mutation, and subscription capabilities"
) 