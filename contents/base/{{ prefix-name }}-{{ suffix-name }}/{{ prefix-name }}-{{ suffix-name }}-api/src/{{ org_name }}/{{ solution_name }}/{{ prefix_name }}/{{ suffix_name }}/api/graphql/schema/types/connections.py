"""
GraphQL connection types for pagination following the Relay specification.

This module implements GraphQL connection patterns for paginated data,
converting from the existing Pydantic pagination models to GraphQL-compliant
connection types.
"""

from typing import List, Optional
import strawberry
import base64
import json

# Import entity types
from .entities import {{ PrefixName }}Type

# Import original pagination models for conversion
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.models.pagination import PageResult


@strawberry.type(description="Information about pagination in a connection")
class PageInfo:
    """
    Information about pagination in a connection.
    
    This follows the Relay specification for cursor-based pagination,
    providing information about whether more pages are available and
    the cursors for the first and last items.
    """
    
    has_next_page: bool = strawberry.field(
        description="When paginating forwards, indicates if more edges exist"
    )
    
    has_previous_page: bool = strawberry.field(
        description="When paginating backwards, indicates if more edges exist"
    )
    
    start_cursor: Optional[str] = strawberry.field(
        description="Cursor corresponding to the first edge in the result",
        default=None
    )
    
    end_cursor: Optional[str] = strawberry.field(
        description="Cursor corresponding to the last edge in the result",
        default=None
    )


@strawberry.type(description="An edge in a {{ PrefixName }} connection")
class {{ PrefixName }}Edge:
    """
    An edge in a {{ PrefixName }} connection.
    
    This wraps a {{ PrefixName }}Type with its cursor for pagination,
    following the Relay specification for edge types.
    """
    
    node: {{ PrefixName }}Type = strawberry.field(
        description="The {{ prefix_name }} at the end of this edge"
    )
    
    cursor: str = strawberry.field(
        description="A cursor for use in pagination"
    )


@strawberry.type(description="A connection to a list of {{ prefix_name }}s")
class {{ PrefixName }}Connection:
    """
    A connection to a list of {{ prefix_name }}s.
    
    This follows the Relay specification for connection types,
    providing paginated access to {{ prefix_name }} entities with
    cursor-based navigation.
    """
    
    edges: List[{{ PrefixName }}Edge] = strawberry.field(
        description="A list of edges containing {{ prefix_name }}s and their cursors"
    )
    
    page_info: PageInfo = strawberry.field(
        description="Information to aid in pagination"
    )
    
    total_count: int = strawberry.field(
        description="The total number of {{ prefix_name }}s available"
    )


# Cursor utility functions
def encode_cursor(value: str) -> str:
    """
    Encode a value as a base64 cursor.
    
    Args:
        value: The value to encode (usually an ID or index)
        
    Returns:
        Base64 encoded cursor string
    """
    cursor_data = {"value": str(value)}
    json_string = json.dumps(cursor_data)
    return base64.b64encode(json_string.encode()).decode()


def decode_cursor(cursor: str) -> str:
    """
    Decode a base64 cursor to get the original value.
    
    Args:
        cursor: Base64 encoded cursor string
        
    Returns:
        The decoded value
        
    Raises:
        ValueError: If the cursor is invalid
    """
    try:
        json_string = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(json_string)
        return cursor_data["value"]
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid cursor: {cursor}") from e


def page_result_to_connection(
    page_result: PageResult[{{ PrefixName }}Type],
    cursor_field: str = "id"
) -> {{ PrefixName }}Connection:
    """
    Convert a PageResult to a GraphQL {{ PrefixName }}Connection.
    
    Args:
        page_result: The paginated result from the service layer
        cursor_field: Field to use for cursor generation (default: "id")
        
    Returns:
        GraphQL connection with edges and page info
    """
    # Create edges from the items
    edges = []
    for item in page_result.items:
        # Get cursor value from the specified field
        cursor_value = getattr(item, cursor_field, None)
        if cursor_value is None:
            # Fallback to item index if cursor field is not available
            cursor_value = str(page_result.items.index(item))
        
        cursor = encode_cursor(str(cursor_value))
        edge = {{ PrefixName }}Edge(node=item, cursor=cursor)
        edges.append(edge)
    
    # Create page info
    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None
    
    page_info = PageInfo(
        has_next_page=page_result.has_next,
        has_previous_page=page_result.has_previous,
        start_cursor=start_cursor,
        end_cursor=end_cursor
    )
    
    # Create and return the connection
    return {{ PrefixName }}Connection(
        edges=edges,
        page_info=page_info,
        total_count=page_result.total_elements
    )


def create_empty_connection() -> {{ PrefixName }}Connection:
    """
    Create an empty {{ PrefixName }}Connection for cases with no results.
    
    Returns:
        Empty connection with appropriate page info
    """
    page_info = PageInfo(
        has_next_page=False,
        has_previous_page=False,
        start_cursor=None,
        end_cursor=None
    )
    
    return {{ PrefixName }}Connection(
        edges=[],
        page_info=page_info,
        total_count=0
    )


# Connection arguments for queries
@strawberry.input(description="Arguments for paginating through {{ prefix_name }}s")
class {{ PrefixName }}ConnectionArgs:
    """
    Input arguments for paginating through {{ prefix_name }}s.
    
    This follows the Relay specification for connection arguments,
    supporting both forward and backward pagination.
    """
    
    first: Optional[int] = strawberry.field(
        description="Returns the first n {{ prefix_name }}s from the list",
        default=None
    )
    
    after: Optional[str] = strawberry.field(
        description="Returns {{ prefix_name }}s after this cursor",
        default=None
    )
    
    last: Optional[int] = strawberry.field(
        description="Returns the last n {{ prefix_name }}s from the list",
        default=None
    )
    
    before: Optional[str] = strawberry.field(
        description="Returns {{ prefix_name }}s before this cursor",
        default=None
    )
    
    def to_page_request(self) -> tuple[int, int]:
        """
        Convert connection args to traditional page/size parameters.
        
        Returns:
            Tuple of (page, size) for use with existing pagination logic
        """
        # Default page size
        size = 10
        page = 0
        
        if self.first is not None:
            size = min(self.first, 100)  # Cap at 100 items
            
            if self.after:
                try:
                    # Decode cursor to get starting position
                    after_value = decode_cursor(self.after)
                    # This is simplified - in a real implementation you'd need
                    # to convert cursor value to page offset
                    page = 0  # For now, start at beginning
                except ValueError:
                    page = 0
        
        elif self.last is not None:
            size = min(self.last, 100)  # Cap at 100 items
            # For 'last' queries, you'd typically need to calculate
            # the appropriate page to get the last N items
            page = 0  # Simplified for now
        
        return page, size 