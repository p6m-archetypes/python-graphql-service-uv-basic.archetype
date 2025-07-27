"""
GraphQL query resolvers for {{ PrefixName }}{{ SuffixName }}.

This module contains resolver functions for all GraphQL queries,
handling data fetching, filtering, pagination, and transformation
from repository entities to GraphQL types.
"""

import uuid
from typing import List, Optional
import strawberry
from sqlalchemy.exc import SQLAlchemyError

# Import GraphQL types
from ..schema.types import (
    {{ PrefixName }}Type,
    {{ PrefixName }}Connection,
    {{ PrefixName }}ConnectionArgs,
    example_dto_to_graphql,
    page_result_to_connection,
    create_empty_connection
)

# Import input types
from ..inputs import (
    {{ PrefixName }}Filter,
    {{ PrefixName }}QueryInput,
    {{ PrefixName }}Sort,
    SortDirection
)

# Import context and entities
from .context import ResolverContext
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.entities.{{ prefix_name }}_entity import {{ PrefixName }}Entity
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.models.pagination import PageResult

# Import API models for conversion
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto


class {{ PrefixName }}QueryResolver:
    """
    Resolver class for {{ PrefixName }} GraphQL queries.
    
    This class contains all resolver methods for querying {{ prefix_name }}
    entities through GraphQL, providing efficient data access with
    DataLoader caching and proper error handling.
    """
    
    @strawberry.field(description="Get a single {{ prefix_name }} by ID")
    async def {{ prefix_name }}(
        self,
        info: strawberry.Info,
        id: strawberry.ID
    ) -> Optional[{{ PrefixName }}Type]:
        """
        Resolve a single {{ prefix_name }} by ID.
        
        Args:
            info: GraphQL execution info containing context
            id: {{ PrefixName }} ID
            
        Returns:
            {{ PrefixName }}Type if found, None otherwise
        """
        context: ResolverContext = info.context
        
        try:
            # Use DataLoader for efficient fetching
            entity = await context.{{ prefix_name }}_loader.load_by_id(str(id))
            
            if not entity:
                return None
            
            # Convert entity to GraphQL type
            return self._entity_to_graphql_type(entity)
            
        except (ValueError, SQLAlchemyError) as e:
            # Log error (in production, use proper logging)
            print(f"Error fetching {{ prefix_name }} {id}: {e}")
            return None
    
    @strawberry.field(description="Get a {{ prefix_name }} by name")
    async def {{ prefix_name }}_by_name(
        self,
        info: strawberry.Info,
        name: str
    ) -> Optional[{{ PrefixName }}Type]:
        """
        Resolve a {{ prefix_name }} by name.
        
        Args:
            info: GraphQL execution info containing context
            name: {{ PrefixName }} name
            
        Returns:
            {{ PrefixName }}Type if found, None otherwise
        """
        context: ResolverContext = info.context
        
        try:
            # Use DataLoader for efficient fetching
            entity = await context.{{ prefix_name }}_loader.load_by_name(name)
            
            if not entity:
                return None
            
            return self._entity_to_graphql_type(entity)
            
        except SQLAlchemyError as e:
            print(f"Error fetching {{ prefix_name }} by name '{name}': {e}")
            return None
    
    @strawberry.field(description="Get a paginated list of {{ prefix_name }}s with filtering and sorting")
    async def {{ prefix_name }}s(
        self,
        info: strawberry.Info,
        connection_args: Optional[{{ PrefixName }}ConnectionArgs] = None,
        filter: Optional[{{ PrefixName }}Filter] = None,
        sort: Optional[List[{{ PrefixName }}Sort]] = None
    ) -> {{ PrefixName }}Connection:
        """
        Resolve a paginated connection of {{ prefix_name }}s with filtering and sorting.
        
        Args:
            info: GraphQL execution info containing context
            connection_args: Pagination arguments (first, after, last, before)
            filter: Filter criteria
            sort: Sort criteria
            
        Returns:
            {{ PrefixName }}Connection with paginated results
        """
        context: ResolverContext = info.context
        
        try:
            # Convert connection args to page parameters
            page, size = self._connection_args_to_page_params(connection_args)
            
            # Apply filtering
            filter_kwargs = self._build_filter_kwargs(filter)
            
            # Apply sorting
            order_by = self._build_order_by(sort)
            
            # Fetch data from repository
            entities = await context.{{ prefix_name }}_repository.get_all(
                limit=size,
                offset=page * size,
                order_by=order_by,
                **filter_kwargs
            )
            
            # Get total count for pagination metadata
            total_count = await context.{{ prefix_name }}_repository.count(**filter_kwargs)
            
            # Convert entities to GraphQL types
            graphql_items = [self._entity_to_graphql_type(entity) for entity in entities]
            
            # Create PageResult for connection conversion
            page_result = PageResult.create(
                items=graphql_items,
                total_elements=total_count,
                page=page,
                size=size
            )
            
            # Convert to GraphQL connection
            return page_result_to_connection(page_result)
            
        except SQLAlchemyError as e:
            print(f"Error fetching {{ prefix_name }}s: {e}")
            return create_empty_connection()
    
    @strawberry.field(description="Search {{ prefix_name }}s by name pattern")
    async def search_{{ prefix_name }}s(
        self,
        info: strawberry.Info,
        query: str,
        limit: Optional[int] = 10
    ) -> List[{{ PrefixName }}Type]:
        """
        Search {{ prefix_name }}s by name pattern.
        
        Args:
            info: GraphQL execution info containing context
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching {{ PrefixName }}Type objects
        """
        context: ResolverContext = info.context
        
        try:
            # Use repository search functionality
            entities = await context.{{ prefix_name }}_repository.search_by_name(query)
            
            # Apply limit
            if limit and len(entities) > limit:
                entities = entities[:limit]
            
            # Convert to GraphQL types
            return [self._entity_to_graphql_type(entity) for entity in entities]
            
        except SQLAlchemyError as e:
            print(f"Error searching {{ prefix_name }}s with query '{query}': {e}")
            return []
    
    @strawberry.field(description="Get {{ prefix_name }}s by status")
    async def {{ prefix_name }}s_by_status(
        self,
        info: strawberry.Info,
        status: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[{{ PrefixName }}Type]:
        """
        Get {{ prefix_name }}s filtered by status.
        
        Args:
            info: GraphQL execution info containing context
            status: Status to filter by
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of {{ PrefixName }}Type objects with the specified status
        """
        context: ResolverContext = info.context
        
        try:
            # Use DataLoader for status-based loading
            entities = await context.{{ prefix_name }}_loader.load_by_status(status)
            
            # Apply pagination manually if needed
            if offset:
                entities = entities[offset:]
            if limit:
                entities = entities[:limit]
            
            return [self._entity_to_graphql_type(entity) for entity in entities]
            
        except SQLAlchemyError as e:
            print(f"Error fetching {{ prefix_name }}s by status '{status}': {e}")
            return []
    
    @strawberry.field(description="Get recently created {{ prefix_name }}s")
    async def recent_{{ prefix_name }}s(
        self,
        info: strawberry.Info,
        days: int = 7,
        limit: Optional[int] = 10
    ) -> List[{{ PrefixName }}Type]:
        """
        Get recently created {{ prefix_name }}s.
        
        Args:
            info: GraphQL execution info containing context
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of recently created {{ PrefixName }}Type objects
        """
        context: ResolverContext = info.context
        
        try:
            entities = await context.{{ prefix_name }}_repository.get_recently_created(
                days=days,
                limit=limit
            )
            
            return [self._entity_to_graphql_type(entity) for entity in entities]
            
        except SQLAlchemyError as e:
            print(f"Error fetching recent {{ prefix_name }}s: {e}")
            return []
    
    @strawberry.field(description="Get {{ prefix_name }} statistics by status")
    async def {{ prefix_name }}_stats(
        self,
        info: strawberry.Info
    ) -> dict:
        """
        Get statistics about {{ prefix_name }}s grouped by status.
        
        Args:
            info: GraphQL execution info containing context
            
        Returns:
            Dictionary mapping status to count
        """
        context: ResolverContext = info.context
        
        try:
            stats = await context.{{ prefix_name }}_repository.count_by_status()
            return stats
            
        except SQLAlchemyError as e:
            print(f"Error fetching {{ prefix_name }} stats: {e}")
            return {}
    
    # Helper methods
    
    def _entity_to_graphql_type(self, entity: {{ PrefixName }}Entity) -> {{ PrefixName }}Type:
        """
        Convert a {{ PrefixName }}Entity to a GraphQL {{ PrefixName }}Type.
        
        Args:
            entity: Database entity
            
        Returns:
            GraphQL type instance
        """
        # Convert entity to ExampleDto first, then to GraphQL type
        dto = ExampleDto(
            id=str(entity.id),
            name=entity.name
        )
        return example_dto_to_graphql(dto)
    
    def _connection_args_to_page_params(
        self, 
        connection_args: Optional[{{ PrefixName }}ConnectionArgs]
    ) -> tuple[int, int]:
        """
        Convert GraphQL connection arguments to page parameters.
        
        Args:
            connection_args: Connection pagination arguments
            
        Returns:
            Tuple of (page, size)
        """
        if not connection_args:
            return 0, 10  # Default page 0, size 10
        
        return connection_args.to_page_request()
    
    def _build_filter_kwargs(self, filter: Optional[{{ PrefixName }}Filter]) -> dict:
        """
        Build repository filter kwargs from GraphQL filter input.
        
        Args:
            filter: GraphQL filter input
            
        Returns:
            Dictionary of filter kwargs for repository
        """
        if not filter or not filter.has_filters():
            return {}
        
        kwargs = {}
        
        # Handle exact name match
        if filter.name:
            kwargs['name'] = filter.name
        
        # Handle name contains (would need custom repository method)
        # For now, we'll use exact match as fallback
        if filter.name_contains and not filter.name:
            # This would require a custom repository method or SQL building
            pass
        
        # Handle ID filtering
        if filter.ids:
            kwargs['id__in'] = [uuid.UUID(id_str) for id_str in filter.ids]
        
        return kwargs
    
    def _build_order_by(self, sort: Optional[List[{{ PrefixName }}Sort]]) -> Optional[str]:
        """
        Build order_by parameter from GraphQL sort input.
        
        Args:
            sort: List of sort criteria
            
        Returns:
            Order by field name (only supports single field for now)
        """
        if not sort or not sort:
            return "name"  # Default sort by name
        
        # For now, only use the first sort criterion
        first_sort = sort[0]
        field_name = first_sort.field.value.lower()
        
        # Map GraphQL field names to entity field names
        field_mapping = {
            "id": "id",
            "name": "name",
            "created_at": "created_at",
            "updated_at": "updated_at"
        }
        
        return field_mapping.get(field_name, "name")


# Create resolver instance for use in schema
{{ prefix_name }}_query_resolver = {{ PrefixName }}QueryResolver() 