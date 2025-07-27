"""
GraphQL subscriptions for {{ PrefixName }}{{ SuffixName }}.

This package provides real-time GraphQL subscriptions including
{{ prefix_name }} change events, batch operations, and subscription statistics.
"""

from .subscription_resolvers import (
    {{ PrefixName }}SubscriptionResolver,
    {{ PrefixName }}ChangeEvent,
    SubscriptionFilter,
    SubscriptionStats
)

__all__ = [
    "{{ PrefixName }}SubscriptionResolver",
    "{{ PrefixName }}ChangeEvent",
    "SubscriptionFilter", 
    "SubscriptionStats"
] 