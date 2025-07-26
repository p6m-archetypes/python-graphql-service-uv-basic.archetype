"""
GraphQL entity types for {{ PrefixName }}{{ SuffixName }}.

This module contains Strawberry GraphQL types that represent the main business entities.
These types are converted from the existing Pydantic models while maintaining field
descriptions and validation logic.
"""

from typing import Optional
import strawberry

# Import the original Pydantic models for reference
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto


@strawberry.type(description="Example entity with core business data")
class {{ PrefixName }}Type:
    """
    GraphQL type representing a {{ PrefixName }} entity.
    
    This type corresponds to the ExampleDto Pydantic model but is optimized
    for GraphQL queries with proper field descriptions and type annotations.
    """
    
    id: Optional[strawberry.ID] = strawberry.field(
        description="Unique identifier for the {{ prefix_name }}"
    )
    
    name: str = strawberry.field(
        description="Name of the {{ prefix_name }}"
    )


@strawberry.type(description="Response payload for {{ prefix_name }} operations")
class {{ PrefixName }}Response:
    """
    Standard response wrapper for {{ prefix_name }} operations.
    
    This provides a consistent response structure for GraphQL mutations
    and queries that return a single {{ prefix_name }}.
    """
    
    {{ prefix_name }}: {{ PrefixName }}Type = strawberry.field(
        description="The {{ prefix_name }} data"
    )
    
    success: bool = strawberry.field(
        description="Whether the operation was successful",
        default=True
    )
    
    message: Optional[str] = strawberry.field(
        description="Optional message about the operation result",
        default=None
    )


@strawberry.type(description="Deletion confirmation response")
class Delete{{ PrefixName }}Response:
    """
    Response type for {{ prefix_name }} deletion operations.
    
    This provides confirmation and details about the deletion operation.
    """
    
    success: bool = strawberry.field(
        description="Whether the deletion was successful"
    )
    
    message: str = strawberry.field(
        description="Confirmation message about the deletion"
    )
    
    deleted_id: Optional[strawberry.ID] = strawberry.field(
        description="ID of the deleted {{ prefix_name }}",
        default=None
    )


# Utility function to convert Pydantic ExampleDto to GraphQL {{ PrefixName }}Type
def example_dto_to_graphql(example_dto: ExampleDto) -> {{ PrefixName }}Type:
    """
    Convert a Pydantic ExampleDto to a GraphQL {{ PrefixName }}Type.
    
    Args:
        example_dto: The Pydantic model instance
        
    Returns:
        GraphQL type instance with the same data
    """
    return {{ PrefixName }}Type(
        id=example_dto.id,
        name=example_dto.name
    )


def graphql_to_example_dto(graphql_type: {{ PrefixName }}Type) -> ExampleDto:
    """
    Convert a GraphQL {{ PrefixName }}Type to a Pydantic ExampleDto.
    
    Args:
        graphql_type: The GraphQL type instance
        
    Returns:
        Pydantic model instance with the same data
    """
    return ExampleDto(
        id=graphql_type.id,
        name=graphql_type.name
    ) 