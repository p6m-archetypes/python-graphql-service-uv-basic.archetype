"""
GraphQL input types for queries, filtering, and sorting.

This module contains Strawberry input types for filtering and sorting
{{ prefix_name }} entities in GraphQL queries.
"""

from typing import Optional, List
import strawberry
from enum import Enum


# Enums for sorting
@strawberry.enum(description="Sort direction for query results")
class SortDirection(Enum):
    """Enumeration for sort directions."""
    
    ASC = "ASC"
    DESC = "DESC"


@strawberry.enum(description="Fields that can be used for sorting {{ prefix_name }}s")
class {{ PrefixName }}SortField(Enum):
    """Fields that can be used for sorting {{ prefix_name }} queries."""
    
    ID = "id"
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


# Input types for filtering
@strawberry.input(description="Filter criteria for {{ prefix_name }} queries")
class {{ PrefixName }}Filter:
    """
    Input type for filtering {{ prefix_name }} queries.
    
    This allows clients to specify various criteria for filtering
    the results of {{ prefix_name }} queries.
    """
    
    # Text-based filters
    name: Optional[str] = strawberry.field(
        description="Filter by {{ prefix_name }} name (exact match)",
        default=None
    )
    
    name_contains: Optional[str] = strawberry.field(
        description="Filter by {{ prefix_name }} name containing this text",
        default=None
    )
    
    name_starts_with: Optional[str] = strawberry.field(
        description="Filter by {{ prefix_name }} name starting with this text",
        default=None
    )
    
    name_ends_with: Optional[str] = strawberry.field(
        description="Filter by {{ prefix_name }} name ending with this text",
        default=None
    )
    
    # ID-based filters
    ids: Optional[List[strawberry.ID]] = strawberry.field(
        description="Filter by specific {{ prefix_name }} IDs",
        default=None
    )
    
    exclude_ids: Optional[List[strawberry.ID]] = strawberry.field(
        description="Exclude specific {{ prefix_name }} IDs from results",
        default=None
    )
    
    # Logical operators
    AND: Optional[List["{{ PrefixName }}Filter"]] = strawberry.field(
        description="All of these conditions must be true",
        default=None
    )
    
    OR: Optional[List["{{ PrefixName }}Filter"]] = strawberry.field(
        description="At least one of these conditions must be true",
        default=None
    )
    
    NOT: Optional["{{ PrefixName }}Filter"] = strawberry.field(
        description="This condition must not be true",
        default=None
    )
    
    def has_filters(self) -> bool:
        """
        Check if this filter contains any actual filtering criteria.
        
        Returns:
            True if any filter criteria are specified
        """
        return any([
            self.name is not None,
            self.name_contains is not None,
            self.name_starts_with is not None,
            self.name_ends_with is not None,
            self.ids is not None,
            self.exclude_ids is not None,
            self.AND is not None,
            self.OR is not None,
            self.NOT is not None,
        ])


@strawberry.input(description="Sort criteria for {{ prefix_name }} queries")
class {{ PrefixName }}Sort:
    """
    Input type for sorting {{ prefix_name }} query results.
    
    This allows clients to specify how they want the results
    of {{ prefix_name }} queries to be sorted.
    """
    
    field: {{ PrefixName }}SortField = strawberry.field(
        description="Field to sort by"
    )
    
    direction: SortDirection = strawberry.field(
        description="Direction to sort (ASC or DESC)",
        default=SortDirection.ASC
    )


@strawberry.input(description="Search criteria for {{ prefix_name }} queries")
class {{ PrefixName }}Search:
    """
    Input type for full-text search of {{ prefix_name }} entities.
    
    This provides more advanced search capabilities beyond simple filtering,
    including fuzzy matching and relevance scoring.
    """
    
    query: str = strawberry.field(
        description="Search query text"
    )
    
    fields: Optional[List[{{ PrefixName }}SortField]] = strawberry.field(
        description="Specific fields to search in (default: all searchable fields)",
        default=None
    )
    
    fuzzy: bool = strawberry.field(
        description="Enable fuzzy matching for approximate results",
        default=False
    )
    
    minimum_score: Optional[float] = strawberry.field(
        description="Minimum relevance score (0.0 - 1.0) for results",
        default=None
    )


# Combined query input
@strawberry.input(description="Complete query input for {{ prefix_name }} operations")
class {{ PrefixName }}QueryInput:
    """
    Complete input type for {{ prefix_name }} queries.
    
    This combines filtering, sorting, searching, and pagination
    into a single comprehensive query input.
    """
    
    filter: Optional[{{ PrefixName }}Filter] = strawberry.field(
        description="Filter criteria to apply",
        default=None
    )
    
    sort: Optional[List[{{ PrefixName }}Sort]] = strawberry.field(
        description="Sort criteria to apply (multiple sorts supported)",
        default=None
    )
    
    search: Optional[{{ PrefixName }}Search] = strawberry.field(
        description="Search criteria to apply",
        default=None
    )
    
    def to_dict(self) -> dict:
        """
        Convert this query input to a dictionary for backend processing.
        
        Returns:
            Dictionary representation suitable for service layer
        """
        result = {}
        
        if self.filter and self.filter.has_filters():
            result['filter'] = self._filter_to_dict(self.filter)
        
        if self.sort:
            result['sort'] = [
                {"field": sort_item.field.value, "direction": sort_item.direction.value}
                for sort_item in self.sort
            ]
        
        if self.search:
            result['search'] = {
                "query": self.search.query,
                "fields": [field.value for field in self.search.fields] if self.search.fields else None,
                "fuzzy": self.search.fuzzy,
                "minimum_score": self.search.minimum_score
            }
        
        return result
    
    def _filter_to_dict(self, filter_obj: {{ PrefixName }}Filter) -> dict:
        """Convert a filter object to dictionary representation."""
        result = {}
        
        # Simple field filters
        if filter_obj.name is not None:
            result['name'] = filter_obj.name
        if filter_obj.name_contains is not None:
            result['name_contains'] = filter_obj.name_contains
        if filter_obj.name_starts_with is not None:
            result['name_starts_with'] = filter_obj.name_starts_with
        if filter_obj.name_ends_with is not None:
            result['name_ends_with'] = filter_obj.name_ends_with
        if filter_obj.ids is not None:
            result['ids'] = [str(id_val) for id_val in filter_obj.ids]
        if filter_obj.exclude_ids is not None:
            result['exclude_ids'] = [str(id_val) for id_val in filter_obj.exclude_ids]
        
        # Logical operators
        if filter_obj.AND is not None:
            result['AND'] = [self._filter_to_dict(and_filter) for and_filter in filter_obj.AND]
        if filter_obj.OR is not None:
            result['OR'] = [self._filter_to_dict(or_filter) for or_filter in filter_obj.OR]
        if filter_obj.NOT is not None:
            result['NOT'] = self._filter_to_dict(filter_obj.NOT)
        
        return result 