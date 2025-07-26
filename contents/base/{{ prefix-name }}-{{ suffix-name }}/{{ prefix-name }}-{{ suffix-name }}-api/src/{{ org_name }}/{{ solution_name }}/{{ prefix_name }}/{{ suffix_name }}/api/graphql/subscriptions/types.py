"""
GraphQL subscription types for {{ PrefixName }}{{ SuffixName }}.

This module defines Strawberry GraphQL types for subscriptions, including
event types, change events, and subscription filters for real-time updates.
"""

from typing import Optional, List
import strawberry
from datetime import datetime
from enum import Enum

# Import base GraphQL types
from ..schema.types import {{ PrefixName }}Type

# Import event bus types
from .event_bus import EventType as BusEventType


@strawberry.enum(description="Type of change event for subscriptions")
class {{ PrefixName }}ChangeType(Enum):
    """Enumeration of change types for {{ prefix_name }} subscriptions."""
    
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    STATUS_CHANGED = "STATUS_CHANGED"
    BATCH_OPERATION = "BATCH_OPERATION"


@strawberry.type(description="A change event for {{ prefix_name }} subscriptions")
class {{ PrefixName }}ChangeEvent:
    """
    Represents a change event that can be subscribed to.
    
    This type wraps the actual {{ prefix_name }} data along with metadata
    about what type of change occurred and when.
    """
    
    event_id: str = strawberry.field(
        description="Unique identifier for this event"
    )
    
    change_type: {{ PrefixName }}ChangeType = strawberry.field(
        description="Type of change that occurred"
    )
    
    {{ prefix_name }}: Optional[{{ PrefixName }}Type] = strawberry.field(
        description="The {{ prefix_name }} data (null for DELETE events)",
        default=None
    )
    
    {{ prefix_name }}_id: Optional[strawberry.ID] = strawberry.field(
        description="ID of the affected {{ prefix_name }}",
        default=None
    )
    
    timestamp: datetime = strawberry.field(
        description="When this change occurred"
    )
    
    user_id: Optional[str] = strawberry.field(
        description="ID of the user who triggered this change",
        default=None
    )
    
    metadata: strawberry.scalars.JSON = strawberry.field(
        description="Additional metadata about the change",
        default_factory=dict
    )
    
    previous_values: Optional[strawberry.scalars.JSON] = strawberry.field(
        description="Previous values for UPDATE events",
        default=None
    )


@strawberry.input(description="Filter criteria for {{ prefix_name }} subscriptions")
class SubscriptionFilter:
    """
    Input type for filtering subscription events.
    
    This allows clients to specify what types of events they want to receive,
    which entities to monitor, and other filtering criteria.
    """
    
    change_types: Optional[List[{{ PrefixName }}ChangeType]] = strawberry.field(
        description="Only receive events of these change types",
        default=None
    )
    
    {{ prefix_name }}_ids: Optional[List[strawberry.ID]] = strawberry.field(
        description="Only receive events for these specific {{ prefix_name }} IDs",
        default=None
    )
    
    user_id: Optional[str] = strawberry.field(
        description="Only receive events triggered by this user",
        default=None
    )
    
    include_batch_operations: bool = strawberry.field(
        description="Whether to include batch operation events",
        default=True
    )
    
    metadata_filters: Optional[strawberry.scalars.JSON] = strawberry.field(
        description="Additional metadata filters as key-value pairs",
        default=None
    )
    
    def to_event_bus_filter(self) -> dict:
        """
        Convert this GraphQL filter to event bus filter criteria.
        
        Returns:
            Dictionary suitable for event bus filtering
        """
        filter_criteria = {}
        
        # Convert change types to event bus types
        if self.change_types:
            bus_event_types = []
            for change_type in self.change_types:
                if change_type == {{ PrefixName }}ChangeType.CREATED:
                    bus_event_types.append(BusEventType.CREATED)
                elif change_type == {{ PrefixName }}ChangeType.UPDATED:
                    bus_event_types.append(BusEventType.UPDATED)
                elif change_type == {{ PrefixName }}ChangeType.DELETED:
                    bus_event_types.append(BusEventType.DELETED)
                elif change_type == {{ PrefixName }}ChangeType.STATUS_CHANGED:
                    bus_event_types.append(BusEventType.STATUS_CHANGED)
                elif change_type == {{ PrefixName }}ChangeType.BATCH_OPERATION:
                    bus_event_types.append(BusEventType.BATCH_OPERATION)
            
            filter_criteria["event_types"] = bus_event_types
        
        # Entity ID filter
        if self.{{ prefix_name }}_ids:
            filter_criteria["entity_ids"] = [str(id) for id in self.{{ prefix_name }}_ids]
        
        # User ID filter
        if self.user_id:
            filter_criteria["user_id"] = self.user_id
        
        # Metadata filters
        if self.metadata_filters:
            filter_criteria["metadata"] = self.metadata_filters
        
        # Batch operations filter
        if not self.include_batch_operations:
            # Exclude batch operations if not wanted
            excluded_types = filter_criteria.get("event_types", [])
            if BusEventType.BATCH_OPERATION not in excluded_types:
                # Add all types except batch operations
                all_types = [t for t in BusEventType if t != BusEventType.BATCH_OPERATION]
                filter_criteria["event_types"] = all_types
        
        return filter_criteria


@strawberry.type(description="Statistics about active subscriptions")
class SubscriptionStats:
    """
    Statistics about the subscription system.
    
    This provides insights into how many subscriptions are active,
    how many events have been published, etc.
    """
    
    active_subscriptions: int = strawberry.field(
        description="Number of currently active subscriptions"
    )
    
    events_published: int = strawberry.field(
        description="Total number of events published"
    )
    
    total_deliveries: int = strawberry.field(
        description="Total number of event deliveries to subscriptions"
    )
    
    subscriptions_created: int = strawberry.field(
        description="Total number of subscriptions created"
    )
    
    subscriptions_cleaned: int = strawberry.field(
        description="Total number of subscriptions cleaned up"
    )
    
    is_running: bool = strawberry.field(
        description="Whether the subscription system is currently running"
    )


@strawberry.type(description="Subscription type for real-time {{ prefix_name }} updates")  
class {{ PrefixName }}SubscriptionType:
    """
    The main subscription type that clients will use.
    
    This provides various subscription endpoints for different types
    of {{ prefix_name }} events and updates.
    """
    
    # Note: The actual subscription resolvers will be defined in subscription_resolvers.py
    # This type serves as a placeholder for the schema definition
    pass


# Utility functions for converting between event bus and GraphQL types

def event_bus_type_to_change_type(bus_type: BusEventType) -> {{ PrefixName }}ChangeType:
    """
    Convert an event bus type to a GraphQL change type.
    
    Args:
        bus_type: Event bus EventType
        
    Returns:
        Corresponding {{ PrefixName }}ChangeType
    """
    mapping = {
        BusEventType.CREATED: {{ PrefixName }}ChangeType.CREATED,
        BusEventType.UPDATED: {{ PrefixName }}ChangeType.UPDATED,
        BusEventType.DELETED: {{ PrefixName }}ChangeType.DELETED,
        BusEventType.STATUS_CHANGED: {{ PrefixName }}ChangeType.STATUS_CHANGED,
        BusEventType.BATCH_OPERATION: {{ PrefixName }}ChangeType.BATCH_OPERATION,
    }
    return mapping.get(bus_type, {{ PrefixName }}ChangeType.UPDATED)


def change_type_to_event_bus_type(change_type: {{ PrefixName }}ChangeType) -> BusEventType:
    """
    Convert a GraphQL change type to an event bus type.
    
    Args:
        change_type: GraphQL {{ PrefixName }}ChangeType
        
    Returns:
        Corresponding event bus EventType
    """
    mapping = {
        {{ PrefixName }}ChangeType.CREATED: BusEventType.CREATED,
        {{ PrefixName }}ChangeType.UPDATED: BusEventType.UPDATED,
        {{ PrefixName }}ChangeType.DELETED: BusEventType.DELETED,
        {{ PrefixName }}ChangeType.STATUS_CHANGED: BusEventType.STATUS_CHANGED,
        {{ PrefixName }}ChangeType.BATCH_OPERATION: BusEventType.BATCH_OPERATION,
    }
    return mapping.get(change_type, BusEventType.UPDATED)


def create_change_event_from_bus_event(
    bus_event,
    previous_values: Optional[dict] = None
) -> {{ PrefixName }}ChangeEvent:
    """
    Create a GraphQL change event from an event bus event.
    
    Args:
        bus_event: Event from the event bus
        previous_values: Previous values for update events
        
    Returns:
        GraphQL {{ PrefixName }}ChangeEvent
    """
    return {{ PrefixName }}ChangeEvent(
        event_id=bus_event.event_id,
        change_type=event_bus_type_to_change_type(bus_event.event_type),
        {{ prefix_name }}=bus_event.entity_data,
        {{ prefix_name }}_id=bus_event.entity_id,
        timestamp=bus_event.timestamp,
        user_id=bus_event.user_id,
        metadata=bus_event.metadata,
        previous_values=previous_values
    ) 