"""
Event bus system for GraphQL subscriptions.

This module provides a centralized event broadcasting system that manages
asyncio queues for real-time GraphQL subscriptions. It supports multiple
event types, filtering, and proper cleanup for disconnected clients.
"""

import asyncio
import uuid
import weakref
from datetime import datetime
from enum import Enum
from typing import Dict, List, Set, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
import logging

# Import GraphQL types
from ..schema.types import {{ PrefixName }}Type

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Enumeration of different event types for subscriptions."""
    
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    STATUS_CHANGED = "STATUS_CHANGED"
    BATCH_OPERATION = "BATCH_OPERATION"


@dataclass
class {{ PrefixName }}Event:
    """
    Event object containing information about {{ prefix_name }} changes.
    
    This represents a single event that can be broadcast to subscribers,
    containing all the necessary information about what changed.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.UPDATED
    entity_id: Optional[str] = None
    entity_data: Optional[{{ PrefixName }}Type] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None  # Who triggered the event
    
    def matches_filter(self, filter_criteria: Dict[str, Any]) -> bool:
        """
        Check if this event matches the given filter criteria.
        
        Args:
            filter_criteria: Dictionary of filter conditions
            
        Returns:
            True if the event matches all filter criteria
        """
        # Event type filter
        if "event_types" in filter_criteria:
            if self.event_type not in filter_criteria["event_types"]:
                return False
        
        # Entity ID filter
        if "entity_ids" in filter_criteria:
            if self.entity_id not in filter_criteria["entity_ids"]:
                return False
        
        # User ID filter (for user-specific events)
        if "user_id" in filter_criteria:
            if self.user_id != filter_criteria["user_id"]:
                return False
        
        # Custom metadata filters
        if "metadata" in filter_criteria:
            for key, value in filter_criteria["metadata"].items():
                if self.metadata.get(key) != value:
                    return False
        
        return True


@dataclass
class Subscription:
    """
    Represents a single subscription with its associated queue and filter.
    """
    
    subscription_id: str
    queue: asyncio.Queue
    filter_criteria: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()


class {{ PrefixName }}EventBus:
    """
    Centralized event bus for managing {{ PrefixName }} subscriptions.
    
    This class handles broadcasting events to subscribers, managing subscription
    lifecycle, and providing filtering capabilities for targeted events.
    """
    
    def __init__(self, max_queue_size: int = 100, cleanup_interval: int = 300):
        """
        Initialize the event bus.
        
        Args:
            max_queue_size: Maximum number of events to queue per subscription
            cleanup_interval: Interval in seconds for cleaning up stale subscriptions
        """
        self.max_queue_size = max_queue_size
        self.cleanup_interval = cleanup_interval
        
        # Store subscriptions by event type for efficient lookup
        self._subscriptions: Dict[EventType, Dict[str, Subscription]] = {
            event_type: {} for event_type in EventType
        }
        
        # Global subscriptions (listen to all events)
        self._global_subscriptions: Dict[str, Subscription] = {}
        
        # Weak references to prevent memory leaks
        self._subscription_refs: Set[weakref.ref] = set()
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self.stats = {
            "events_published": 0,
            "subscriptions_created": 0,
            "subscriptions_cleaned": 0,
            "total_deliveries": 0
        }
    
    async def start(self):
        """Start the event bus and background cleanup task."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("{{ PrefixName }}EventBus started")
    
    async def stop(self):
        """Stop the event bus and cleanup all subscriptions."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all subscription queues
        await self._cleanup_all_subscriptions()
        logger.info("{{ PrefixName }}EventBus stopped")
    
    def subscribe(
        self,
        event_types: Optional[List[EventType]] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
        subscription_id: Optional[str] = None
    ) -> tuple[str, AsyncGenerator[{{ PrefixName }}Event, None]]:
        """
        Subscribe to {{ prefix_name }} events.
        
        Args:
            event_types: List of event types to subscribe to (None for all)
            filter_criteria: Additional filter criteria
            subscription_id: Optional custom subscription ID
            
        Returns:
            Tuple of (subscription_id, event_generator)
        """
        if subscription_id is None:
            subscription_id = str(uuid.uuid4())
        
        if filter_criteria is None:
            filter_criteria = {}
        
        # Create queue for this subscription
        queue = asyncio.Queue(maxsize=self.max_queue_size)
        subscription = Subscription(
            subscription_id=subscription_id,
            queue=queue,
            filter_criteria=filter_criteria
        )
        
        # Register subscription
        if event_types is None:
            # Global subscription (all events)
            self._global_subscriptions[subscription_id] = subscription
        else:
            # Specific event type subscriptions
            for event_type in event_types:
                self._subscriptions[event_type][subscription_id] = subscription
        
        self.stats["subscriptions_created"] += 1
        logger.debug(f"Created subscription {subscription_id} for events: {event_types}")
        
        # Return subscription ID and generator
        return subscription_id, self._event_generator(subscription)
    
    async def _event_generator(self, subscription: Subscription) -> AsyncGenerator[{{ PrefixName }}Event, None]:
        """
        Generate events for a specific subscription.
        
        Args:
            subscription: The subscription to generate events for
            
        Yields:
            {{ PrefixName }}Event objects that match the subscription criteria
        """
        try:
            while True:
                # Wait for next event
                event = await subscription.queue.get()
                subscription.update_activity()
                
                # Yield event to subscriber
                yield event
                
                # Mark task as done
                subscription.queue.task_done()
                
        except asyncio.CancelledError:
            logger.debug(f"Subscription {subscription.subscription_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in subscription {subscription.subscription_id}: {e}")
            raise
        finally:
            # Cleanup subscription
            await self._cleanup_subscription(subscription.subscription_id)
    
    async def publish(self, event: {{ PrefixName }}Event) -> int:
        """
        Publish an event to all matching subscriptions.
        
        Args:
            event: The event to publish
            
        Returns:
            Number of subscriptions the event was delivered to
        """
        if not self._running:
            logger.warning("Event bus not running, event dropped")
            return 0
        
        delivered_count = 0
        
        # Deliver to global subscriptions
        for subscription in self._global_subscriptions.values():
            if event.matches_filter(subscription.filter_criteria):
                delivered_count += await self._deliver_event(event, subscription)
        
        # Deliver to specific event type subscriptions
        event_subscriptions = self._subscriptions.get(event.event_type, {})
        for subscription in event_subscriptions.values():
            if event.matches_filter(subscription.filter_criteria):
                delivered_count += await self._deliver_event(event, subscription)
        
        self.stats["events_published"] += 1
        self.stats["total_deliveries"] += delivered_count
        
        logger.debug(f"Published event {event.event_id} to {delivered_count} subscriptions")
        return delivered_count
    
    async def _deliver_event(self, event: {{ PrefixName }}Event, subscription: Subscription) -> int:
        """
        Deliver an event to a specific subscription.
        
        Args:
            event: Event to deliver
            subscription: Target subscription
            
        Returns:
            1 if delivered successfully, 0 if failed
        """
        try:
            # Non-blocking put with timeout
            subscription.queue.put_nowait(event)
            return 1
        except asyncio.QueueFull:
            logger.warning(f"Queue full for subscription {subscription.subscription_id}, dropping event")
            return 0
        except Exception as e:
            logger.error(f"Failed to deliver event to subscription {subscription.subscription_id}: {e}")
            return 0
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            True if subscription was found and removed
        """
        return await self._cleanup_subscription(subscription_id)
    
    async def _cleanup_subscription(self, subscription_id: str) -> bool:
        """
        Clean up a specific subscription.
        
        Args:
            subscription_id: ID of subscription to clean up
            
        Returns:
            True if subscription was found and cleaned up
        """
        found = False
        
        # Remove from global subscriptions
        if subscription_id in self._global_subscriptions:
            del self._global_subscriptions[subscription_id]
            found = True
        
        # Remove from event type subscriptions
        for event_type_subs in self._subscriptions.values():
            if subscription_id in event_type_subs:
                del event_type_subs[subscription_id]
                found = True
        
        if found:
            self.stats["subscriptions_cleaned"] += 1
            logger.debug(f"Cleaned up subscription {subscription_id}")
        
        return found
    
    async def _cleanup_loop(self):
        """Background task for cleaning up stale subscriptions."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_stale_subscriptions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_stale_subscriptions(self):
        """Clean up subscriptions that haven't been active recently."""
        cutoff_time = datetime.utcnow().timestamp() - (self.cleanup_interval * 2)
        stale_ids = []
        
        # Check global subscriptions
        for sub_id, subscription in self._global_subscriptions.items():
            if subscription.last_activity.timestamp() < cutoff_time:
                stale_ids.append(sub_id)
        
        # Check event type subscriptions
        for event_type_subs in self._subscriptions.values():
            for sub_id, subscription in event_type_subs.items():
                if subscription.last_activity.timestamp() < cutoff_time:
                    stale_ids.append(sub_id)
        
        # Clean up stale subscriptions
        for sub_id in stale_ids:
            await self._cleanup_subscription(sub_id)
        
        if stale_ids:
            logger.info(f"Cleaned up {len(stale_ids)} stale subscriptions")
    
    async def _cleanup_all_subscriptions(self):
        """Clean up all subscriptions."""
        all_ids = []
        
        # Collect all subscription IDs
        all_ids.extend(self._global_subscriptions.keys())
        for event_type_subs in self._subscriptions.values():
            all_ids.extend(event_type_subs.keys())
        
        # Clean up all subscriptions
        for sub_id in all_ids:
            await self._cleanup_subscription(sub_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        active_subscriptions = len(self._global_subscriptions)
        for event_type_subs in self._subscriptions.values():
            active_subscriptions += len(event_type_subs)
        
        return {
            **self.stats,
            "active_subscriptions": active_subscriptions,
            "is_running": self._running
        }


# Global event bus instance
_event_bus: Optional[{{ PrefixName }}EventBus] = None


def get_event_bus() -> {{ PrefixName }}EventBus:
    """
    Get the global event bus instance.
    
    Returns:
        Global {{ PrefixName }}EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = {{ PrefixName }}EventBus()
    return _event_bus


async def initialize_event_bus() -> {{ PrefixName }}EventBus:
    """
    Initialize and start the global event bus.
    
    Returns:
        Started event bus instance
    """
    event_bus = get_event_bus()
    await event_bus.start()
    return event_bus


async def shutdown_event_bus():
    """Shutdown the global event bus."""
    global _event_bus
    if _event_bus:
        await _event_bus.stop()
        _event_bus = None 