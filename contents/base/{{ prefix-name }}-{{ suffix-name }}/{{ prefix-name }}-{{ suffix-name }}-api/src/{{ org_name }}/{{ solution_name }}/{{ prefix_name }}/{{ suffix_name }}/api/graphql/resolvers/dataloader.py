"""
DataLoader implementations for efficient data fetching.

This module provides DataLoader implementations that batch database queries
to prevent N+1 query problems in GraphQL resolvers.
"""

import uuid
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Import Strawberry DataLoader
try:
    from strawberry.dataloader import DataLoader
    DATALOADER_AVAILABLE = True
except ImportError:
    # Fallback for environments without Strawberry
    DATALOADER_AVAILABLE = False
    
    class DataLoader:
        """Mock DataLoader for environments without Strawberry."""
        def __init__(self, load_fn):
            self.load_fn = load_fn
        
        async def load(self, key):
            return await self.load_fn([key])[0]
        
        async def load_many(self, keys):
            return await self.load_fn(keys)
        
        def clear(self, key):
            pass
        
        def clear_all(self):
            pass

from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories import {{ PrefixName }}Repository
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.entities.{{ prefix_name }}_entity import {{ PrefixName }}Entity


class {{ PrefixName }}DataLoader:
    """
    DataLoader for {{ PrefixName }} entities.
    
    This class provides efficient batch loading of {{ prefix_name }} entities
    to prevent N+1 query problems when resolving GraphQL fields.
    """
    
    def __init__(self, repository: {{ PrefixName }}Repository):
        """
        Initialize the {{ PrefixName }} DataLoader.
        
        Args:
            repository: {{ PrefixName }} repository for data access
        """
        self.repository = repository
        
        # Create individual DataLoaders for different load patterns
        self._by_id_loader = DataLoader(load_fn=self._load_by_ids)
        self._by_name_loader = DataLoader(load_fn=self._load_by_names)
        self._by_status_loader = DataLoader(load_fn=self._load_by_status_batch)
    
    async def _load_by_ids(self, ids: List[str]) -> List[Optional[{{ PrefixName }}Entity]]:
        """
        Batch load {{ prefix_name }}s by their IDs.
        
        Args:
            ids: List of {{ prefix_name }} ID strings
            
        Returns:
            List of {{ PrefixName }}Entity objects in the same order as IDs,
            with None for IDs that don't exist
        """
        # Convert string IDs to UUIDs
        try:
            uuid_ids = [uuid.UUID(id_str) for id_str in ids]
        except ValueError as e:
            # Return None for all invalid UUIDs
            return [None] * len(ids)
        
        # Get entities using the repository's bulk fetch capability
        entities = await self.repository.get_all()
        entities_by_id = {str(entity.id): entity for entity in entities if entity.id in uuid_ids}
        
        # Return entities in the same order as requested IDs
        return [entities_by_id.get(id_str) for id_str in ids]
    
    async def _load_by_names(self, names: List[str]) -> List[Optional[{{ PrefixName }}Entity]]:
        """
        Batch load {{ prefix_name }}s by their names.
        
        Args:
            names: List of {{ prefix_name }} names
            
        Returns:
            List of {{ PrefixName }}Entity objects in the same order as names,
            with None for names that don't exist
        """
        # Get all entities that match any of the names
        all_entities = await self.repository.get_all()
        entities_by_name = {entity.name: entity for entity in all_entities if entity.name in names}
        
        # Return entities in the same order as requested names
        return [entities_by_name.get(name) for name in names]
    
    async def _load_by_status_batch(self, statuses: List[str]) -> List[List[{{ PrefixName }}Entity]]:
        """
        Batch load {{ prefix_name }}s grouped by status.
        
        Args:
            statuses: List of status values
            
        Returns:
            List of lists, where each inner list contains entities with the corresponding status
        """
        # Get all entities
        all_entities = await self.repository.get_all()
        
        # Group entities by status
        entities_by_status = defaultdict(list)
        for entity in all_entities:
            if entity.status in statuses:
                entities_by_status[entity.status].append(entity)
        
        # Return lists in the same order as requested statuses
        return [entities_by_status.get(status, []) for status in statuses]
    
    async def load_by_id(self, id_str: str) -> Optional[{{ PrefixName }}Entity]:
        """
        Load a single {{ prefix_name }} by ID using DataLoader caching.
        
        Args:
            id_str: {{ PrefixName }} ID as string
            
        Returns:
            {{ PrefixName }}Entity if found, None otherwise
        """
        return await self._by_id_loader.load(id_str)
    
    async def load_many_by_ids(self, ids: List[str]) -> List[Optional[{{ PrefixName }}Entity]]:
        """
        Load multiple {{ prefix_name }}s by IDs using DataLoader caching.
        
        Args:
            ids: List of {{ prefix_name }} ID strings
            
        Returns:
            List of {{ PrefixName }}Entity objects (may contain None for missing entities)
        """
        return await self._by_id_loader.load_many(ids)
    
    async def load_by_name(self, name: str) -> Optional[{{ PrefixName }}Entity]:
        """
        Load a single {{ prefix_name }} by name using DataLoader caching.
        
        Args:
            name: {{ PrefixName }} name
            
        Returns:
            {{ PrefixName }}Entity if found, None otherwise
        """
        return await self._by_name_loader.load(name)
    
    async def load_many_by_names(self, names: List[str]) -> List[Optional[{{ PrefixName }}Entity]]:
        """
        Load multiple {{ prefix_name }}s by names using DataLoader caching.
        
        Args:
            names: List of {{ prefix_name }} names
            
        Returns:
            List of {{ PrefixName }}Entity objects (may contain None for missing entities)
        """
        return await self._by_name_loader.load_many(names)
    
    async def load_by_status(self, status: str) -> List[{{ PrefixName }}Entity]:
        """
        Load {{ prefix_name }}s by status using DataLoader caching.
        
        Args:
            status: Status value to filter by
            
        Returns:
            List of {{ PrefixName }}Entity objects with the specified status
        """
        results = await self._by_status_loader.load(status)
        return results if results else []
    
    def clear_by_id(self, id_str: str) -> None:
        """
        Clear a specific {{ prefix_name }} from the DataLoader cache.
        
        Args:
            id_str: {{ PrefixName }} ID as string
        """
        self._by_id_loader.clear(id_str)
    
    def clear_by_name(self, name: str) -> None:
        """
        Clear a specific {{ prefix_name }} from the name-based DataLoader cache.
        
        Args:
            name: {{ PrefixName }} name
        """
        self._by_name_loader.clear(name)
    
    def clear_all(self) -> None:
        """Clear all DataLoader caches."""
        self._by_id_loader.clear_all()
        self._by_name_loader.clear_all()
        self._by_status_loader.clear_all()


def create_dataloaders(repositories: Dict[str, any]) -> Dict[str, any]:
    """
    Factory function to create all DataLoaders from repositories.
    
    Args:
        repositories: Dictionary of repository instances
        
    Returns:
        Dictionary of DataLoader instances
    """
    dataloaders = {}
    
    if "{{ prefix_name }}_repository" in repositories:
        dataloaders["{{ prefix_name }}_loader"] = {{ PrefixName }}DataLoader(
            repositories["{{ prefix_name }}_repository"]
        )
    
    return dataloaders


# Helper functions for DataLoader key generation
def generate_cache_key(entity_type: str, field: str, value: str) -> str:
    """
    Generate a consistent cache key for DataLoader operations.
    
    Args:
        entity_type: Type of entity (e.g., "{{ prefix_name }}")
        field: Field name (e.g., "id", "name")
        value: Field value
        
    Returns:
        Formatted cache key
    """
    return f"{entity_type}:{field}:{value}"


def batch_keys_by_type(keys: List[str]) -> Dict[str, List[str]]:
    """
    Group DataLoader keys by their type for more efficient batching.
    
    Args:
        keys: List of cache keys
        
    Returns:
        Dictionary grouping keys by their entity type
    """
    batched = defaultdict(list)
    
    for key in keys:
        parts = key.split(":", 2)
        if len(parts) >= 2:
            entity_type = parts[0]
            batched[entity_type].append(key)
    
    return dict(batched) 