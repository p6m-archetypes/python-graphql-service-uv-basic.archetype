"""
GraphQL subscription resolvers for {{ PrefixName }}{{ SuffixName }}.

This module contains resolver functions for all GraphQL subscriptions,
providing real-time updates for {{ prefix_name }} events through WebSocket
connections with comprehensive filtering and error handling.
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator, List
import strawberry

# Import subscription types
from .types import (
    {{ PrefixName }}ChangeEvent,
    SubscriptionFilter,
    SubscriptionStats,
    create_change_event_from_bus_event
)

# Import event bus
from .event_bus import (
    get_event_bus,
    {{ PrefixName }}Event,
    EventType
)

# Import resolver context
from ..resolvers.context import ResolverContext

logger = logging.getLogger(__name__)


class {{ PrefixName }}SubscriptionResolver:
    """
    Resolver class for {{ PrefixName }} GraphQL subscriptions.
    
    This class contains all resolver methods for real-time subscriptions,
    providing efficient event streaming with filtering, error handling,
    and proper connection management.
    """
    
    @strawberry.subscription(description="Subscribe to all {{ prefix_name }} changes")
    async def {{ prefix_name }}_changes(
        self,
        info: strawberry.Info,
        filter: Optional[SubscriptionFilter] = None
    ) -> AsyncGenerator[{{ PrefixName }}ChangeEvent, None]:
        """
        Subscribe to all types of {{ prefix_name }} changes.
        
        This subscription provides a comprehensive stream of all {{ prefix_name }}
        events including creates, updates, deletes, and status changes.
        
        Args:
            info: GraphQL execution info containing context
            filter: Optional filter criteria to limit events
            
        Yields:
            {{ PrefixName }}ChangeEvent objects for matching events
        """
        context: ResolverContext = info.context
        event_bus = get_event_bus()
        
        # Convert GraphQL filter to event bus filter
        filter_criteria = filter.to_event_bus_filter() if filter else {}
        
        # Subscribe to all event types
        subscription_id, event_generator = event_bus.subscribe(
            event_types=None,  # All event types
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Client subscribed to all {{ prefix_name }} changes (subscription: {subscription_id})")
        
        try:
            async for bus_event in event_generator:
                # Convert bus event to GraphQL event
                change_event = create_change_event_from_bus_event(bus_event)
                
                # Additional authorization check if needed
                if await self._is_authorized_for_event(context, bus_event):
                    yield change_event
                
        except asyncio.CancelledError:
            logger.info(f"Subscription {subscription_id} cancelled by client")
            raise
        except Exception as e:
            logger.error(f"Error in subscription {subscription_id}: {e}")
            # Optionally yield error event
            yield self._create_error_event(str(e))
        finally:
            # Cleanup handled by event bus
            logger.debug(f"Subscription {subscription_id} cleanup complete")
    
    @strawberry.subscription(description="Subscribe to {{ prefix_name }} creation events")
    async def {{ prefix_name }}_created(
        self,
        info: strawberry.Info,
        filter: Optional[SubscriptionFilter] = None
    ) -> AsyncGenerator[{{ PrefixName }}ChangeEvent, None]:
        """
        Subscribe specifically to {{ prefix_name }} creation events.
        
        This subscription only delivers events when new {{ prefix_name }}s
        are created, useful for real-time notifications of new entities.
        
        Args:
            info: GraphQL execution info containing context
            filter: Optional filter criteria to limit events
            
        Yields:
            {{ PrefixName }}ChangeEvent objects for creation events
        """
        context: ResolverContext = info.context
        event_bus = get_event_bus()
        
        # Convert GraphQL filter and ensure only creation events
        filter_criteria = filter.to_event_bus_filter() if filter else {}
        
        # Subscribe only to creation events
        subscription_id, event_generator = event_bus.subscribe(
            event_types=[EventType.CREATED],
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Client subscribed to {{ prefix_name }} creation events (subscription: {subscription_id})")
        
        try:
            async for bus_event in event_generator:
                # Convert and authorize
                change_event = create_change_event_from_bus_event(bus_event)
                
                if await self._is_authorized_for_event(context, bus_event):
                    yield change_event
                    
        except asyncio.CancelledError:
            logger.info(f"Creation subscription {subscription_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in creation subscription {subscription_id}: {e}")
            yield self._create_error_event(str(e))
    
    @strawberry.subscription(description="Subscribe to {{ prefix_name }} update events")
    async def {{ prefix_name }}_updated(
        self,
        info: strawberry.Info,
        {{ prefix_name }}_id: Optional[strawberry.ID] = None,
        filter: Optional[SubscriptionFilter] = None
    ) -> AsyncGenerator[{{ PrefixName }}ChangeEvent, None]:
        """
        Subscribe to {{ prefix_name }} update events.
        
        This subscription delivers events when existing {{ prefix_name }}s
        are modified. Can be filtered to specific entities.
        
        Args:
            info: GraphQL execution info containing context
            {{ prefix_name }}_id: Optional specific {{ prefix_name }} ID to monitor
            filter: Optional additional filter criteria
            
        Yields:
            {{ PrefixName }}ChangeEvent objects for update events
        """
        context: ResolverContext = info.context
        event_bus = get_event_bus()
        
        # Build filter criteria
        filter_criteria = filter.to_event_bus_filter() if filter else {}
        
        # Add specific entity ID filter if provided
        if {{ prefix_name }}_id:
            entity_ids = filter_criteria.get("entity_ids", [])
            entity_ids.append(str({{ prefix_name }}_id))
            filter_criteria["entity_ids"] = entity_ids
        
        # Subscribe to update and status change events
        subscription_id, event_generator = event_bus.subscribe(
            event_types=[EventType.UPDATED, EventType.STATUS_CHANGED],
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Client subscribed to {{ prefix_name }} updates (subscription: {subscription_id}, entity: {{{ prefix_name }}_id})")
        
        try:
            async for bus_event in event_generator:
                # Include previous values for update events
                previous_values = bus_event.metadata.get("previous_values")
                change_event = create_change_event_from_bus_event(bus_event, previous_values)
                
                if await self._is_authorized_for_event(context, bus_event):
                    yield change_event
                    
        except asyncio.CancelledError:
            logger.info(f"Update subscription {subscription_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in update subscription {subscription_id}: {e}")
            yield self._create_error_event(str(e))
    
    @strawberry.subscription(description="Subscribe to {{ prefix_name }} deletion events")
    async def {{ prefix_name }}_deleted(
        self,
        info: strawberry.Info,
        filter: Optional[SubscriptionFilter] = None
    ) -> AsyncGenerator[{{ PrefixName }}ChangeEvent, None]:
        """
        Subscribe to {{ prefix_name }} deletion events.
        
        This subscription delivers events when {{ prefix_name }}s are deleted.
        The event will contain the ID but not the full entity data.
        
        Args:
            info: GraphQL execution info containing context
            filter: Optional filter criteria to limit events
            
        Yields:
            {{ PrefixName }}ChangeEvent objects for deletion events
        """
        context: ResolverContext = info.context
        event_bus = get_event_bus()
        
        # Convert GraphQL filter
        filter_criteria = filter.to_event_bus_filter() if filter else {}
        
        # Subscribe only to deletion events
        subscription_id, event_generator = event_bus.subscribe(
            event_types=[EventType.DELETED],
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Client subscribed to {{ prefix_name }} deletion events (subscription: {subscription_id})")
        
        try:
            async for bus_event in event_generator:
                change_event = create_change_event_from_bus_event(bus_event)
                
                if await self._is_authorized_for_event(context, bus_event):
                    yield change_event
                    
        except asyncio.CancelledError:
            logger.info(f"Deletion subscription {subscription_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in deletion subscription {subscription_id}: {e}")
            yield self._create_error_event(str(e))
    
    @strawberry.subscription(description="Subscribe to batch operation events")
    async def {{ prefix_name }}_batch_operations(
        self,
        info: strawberry.Info,
        filter: Optional[SubscriptionFilter] = None
    ) -> AsyncGenerator[{{ PrefixName }}ChangeEvent, None]:
        """
        Subscribe to batch operation events.
        
        This subscription delivers events when batch operations are performed
        on multiple {{ prefix_name }}s simultaneously.
        
        Args:
            info: GraphQL execution info containing context
            filter: Optional filter criteria to limit events
            
        Yields:
            {{ PrefixName }}ChangeEvent objects for batch operation events
        """
        context: ResolverContext = info.context
        event_bus = get_event_bus()
        
        # Convert GraphQL filter
        filter_criteria = filter.to_event_bus_filter() if filter else {}
        
        # Subscribe only to batch operation events
        subscription_id, event_generator = event_bus.subscribe(
            event_types=[EventType.BATCH_OPERATION],
            filter_criteria=filter_criteria
        )
        
        logger.info(f"Client subscribed to {{ prefix_name }} batch operations (subscription: {subscription_id})")
        
        try:
            async for bus_event in event_generator:
                change_event = create_change_event_from_bus_event(bus_event)
                
                if await self._is_authorized_for_event(context, bus_event):
                    yield change_event
                    
        except asyncio.CancelledError:
            logger.info(f"Batch operations subscription {subscription_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in batch operations subscription {subscription_id}: {e}")
            yield self._create_error_event(str(e))
    
    @strawberry.subscription(description="Get real-time subscription statistics")
    async def subscription_stats(
        self,
        info: strawberry.Info,
        interval_seconds: int = 10
    ) -> AsyncGenerator[SubscriptionStats, None]:
        """
        Subscribe to real-time statistics about the subscription system.
        
        This is useful for monitoring and debugging subscription performance.
        
        Args:
            info: GraphQL execution info containing context
            interval_seconds: How often to emit statistics (default: 10 seconds)
            
        Yields:
            SubscriptionStats objects with current system statistics
        """
        context: ResolverContext = info.context
        
        # Check if user is authorized for stats (admin only)
        if not await self._is_authorized_for_stats(context):
            logger.warning(f"Unauthorized stats subscription attempt from user {context.user_id}")
            return
        
        event_bus = get_event_bus()
        
        logger.info(f"Client subscribed to subscription stats (interval: {interval_seconds}s)")
        
        try:
            while True:
                # Get current stats from event bus
                stats_data = event_bus.get_stats()
                
                # Convert to GraphQL type
                stats = SubscriptionStats(
                    active_subscriptions=stats_data["active_subscriptions"],
                    events_published=stats_data["events_published"],
                    total_deliveries=stats_data["total_deliveries"],
                    subscriptions_created=stats_data["subscriptions_created"],
                    subscriptions_cleaned=stats_data["subscriptions_cleaned"],
                    is_running=stats_data["is_running"]
                )
                
                yield stats
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("Stats subscription cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in stats subscription: {e}")
    
    # Helper methods
    
    async def _is_authorized_for_event(
        self, 
        context: ResolverContext, 
        event: {{ PrefixName }}Event
    ) -> bool:
        """
        Check if the current user is authorized to receive this event.
        
        Args:
            context: Resolver context with user information
            event: Event to check authorization for
            
        Returns:
            True if authorized to receive the event
        """
        # Basic implementation - can be extended with more complex rules
        
        # Always allow if no authentication required
        if not context.is_authenticated():
            return True
        
        # User can always see their own events
        if event.user_id == context.user_id:
            return True
        
        # Admin users can see all events
        if context.has_role("admin"):
            return True
        
        # Default: allow all events for authenticated users
        # In a real application, you might want to implement more specific rules
        return True
    
    async def _is_authorized_for_stats(self, context: ResolverContext) -> bool:
        """
        Check if the current user is authorized to view subscription statistics.
        
        Args:
            context: Resolver context with user information
            
        Returns:
            True if authorized to view stats
        """
        # Only admin users can view stats
        return context.has_role("admin")
    
    def _create_error_event(self, error_message: str) -> {{ PrefixName }}ChangeEvent:
        """
        Create an error event for subscription error handling.
        
        Args:
            error_message: Error message to include
            
        Returns:
            {{ PrefixName }}ChangeEvent representing the error
        """
        from .types import {{ PrefixName }}ChangeType
        from datetime import datetime
        import uuid
        
        return {{ PrefixName }}ChangeEvent(
            event_id=str(uuid.uuid4()),
            change_type={{ PrefixName }}ChangeType.UPDATED,  # Use UPDATED as default
            {{ prefix_name }}=None,
            {{ prefix_name }}_id=None,
            timestamp=datetime.utcnow(),
            user_id=None,
            metadata={"error": True, "message": error_message},
            previous_values=None
        )


# Create resolver instance for use in schema
{{ prefix_name }}_subscription_resolver = {{ PrefixName }}SubscriptionResolver() 