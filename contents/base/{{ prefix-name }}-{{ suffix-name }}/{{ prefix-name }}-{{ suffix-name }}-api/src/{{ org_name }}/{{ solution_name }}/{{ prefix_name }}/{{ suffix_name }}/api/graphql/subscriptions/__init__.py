"""
GraphQL subscriptions package for {{ PrefixName }}{{ SuffixName }}.

This package provides real-time subscription capabilities for the GraphQL API,
including WebSocket support, event broadcasting, and subscription resolvers.
"""

from .event_bus import (
    {{ PrefixName }}EventBus,
    {{ PrefixName }}Event,
    EventType,
    get_event_bus
)
from .subscription_resolvers import {{ PrefixName }}SubscriptionResolver
from .types import (
    {{ PrefixName }}SubscriptionType,
    {{ PrefixName }}ChangeEvent,
    SubscriptionFilter
)

__all__ = [
    "{{ PrefixName }}EventBus",
    "{{ PrefixName }}Event", 
    "EventType",
    "get_event_bus",
    "{{ PrefixName }}SubscriptionResolver",
    "{{ PrefixName }}SubscriptionType",
    "{{ PrefixName }}ChangeEvent",
    "SubscriptionFilter"
] 