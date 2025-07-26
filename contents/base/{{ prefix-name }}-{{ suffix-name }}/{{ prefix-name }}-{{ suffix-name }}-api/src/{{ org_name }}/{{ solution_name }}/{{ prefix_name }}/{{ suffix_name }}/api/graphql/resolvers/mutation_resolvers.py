"""
GraphQL mutation resolvers for {{ PrefixName }}{{ SuffixName }}.

This module contains resolver functions for all GraphQL mutations,
handling create, update, and delete operations with proper validation,
error handling, and transaction management.
"""

import uuid
from typing import List, Optional, Dict, Any
import strawberry
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# Import GraphQL types
from ..schema.types import (
    {{ PrefixName }}Response,
    Delete{{ PrefixName }}Response,
    example_dto_to_graphql
)

# Import input types
from ..inputs import (
    Create{{ PrefixName }}Input,
    Update{{ PrefixName }}Input,
    Delete{{ PrefixName }}Input,
    CreateMultiple{{ PrefixName }}Input,
    UpdateMultiple{{ PrefixName }}Input
)

# Import context and validation
from .context import ResolverContext
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.entities.{{ prefix_name }}_entity import {{ PrefixName }}Entity
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto

# Import core validation services
try:
    from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core.services import ValidationService
    VALIDATION_SERVICE_AVAILABLE = True
except ImportError:
    VALIDATION_SERVICE_AVAILABLE = False
    print("⚠️  ValidationService not available - using basic validation")


class {{ PrefixName }}MutationResolver:
    """
    Resolver class for {{ PrefixName }} GraphQL mutations.
    
    This class contains all resolver methods for creating, updating, and deleting
    {{ prefix_name }} entities through GraphQL mutations, with comprehensive
    validation, error handling, and transaction support.
    """
    
    @strawberry.mutation(description="Create a new {{ prefix_name }}")
    async def create_{{ prefix_name }}(
        self,
        info: strawberry.Info,
        input: Create{{ PrefixName }}Input
    ) -> {{ PrefixName }}Response:
        """
        Create a new {{ prefix_name }} entity.
        
        Args:
            info: GraphQL execution info containing context
            input: Input data for creating the {{ prefix_name }}
            
        Returns:
            {{ PrefixName }}Response with the created entity or error information
        """
        context: ResolverContext = info.context
        
        try:
            # Validate input data
            validation_result = await self._validate_create_input(input, context)
            if not validation_result["is_valid"]:
                return {{ PrefixName }}Response(
                    success=False,
                    message="Validation failed",
                    {{ prefix_name }}=None
                )
            
            # Convert input to entity data
            entity_data = self._input_to_entity_data(input)
            
            # Check for duplicate names
            existing = await context.{{ prefix_name }}_repository.get_by_name(input.name)
            if existing:
                return {{ PrefixName }}Response(
                    success=False,
                    message=f"{{ PrefixName }} with name '{input.name}' already exists",
                    {{ prefix_name }}=None
                )
            
            # Create the entity
            created_entity = await context.{{ prefix_name }}_repository.create(**entity_data)
            
            # Clear DataLoader caches
            context.{{ prefix_name }}_loader.clear_by_name(input.name)
            context.{{ prefix_name }}_loader.clear_by_id(str(created_entity.id))
            
            # Convert to GraphQL type
            graphql_type = self._entity_to_graphql_type(created_entity)
            
            return {{ PrefixName }}Response(
                success=True,
                message=f"{{ PrefixName }} '{input.name}' created successfully",
                {{ prefix_name }}=graphql_type
            )
            
        except IntegrityError as e:
            await context.session.rollback()
            return {{ PrefixName }}Response(
                success=False,
                message="A {{ prefix_name }} with this information already exists",
                {{ prefix_name }}=None
            )
        except SQLAlchemyError as e:
            await context.session.rollback()
            print(f"Database error creating {{ prefix_name }}: {e}")
            return {{ PrefixName }}Response(
                success=False,
                message="Database error occurred while creating {{ prefix_name }}",
                {{ prefix_name }}=None
            )
        except Exception as e:
            await context.session.rollback()
            print(f"Unexpected error creating {{ prefix_name }}: {e}")
            return {{ PrefixName }}Response(
                success=False,
                message="An unexpected error occurred",
                {{ prefix_name }}=None
            )
    
    @strawberry.mutation(description="Update an existing {{ prefix_name }}")
    async def update_{{ prefix_name }}(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: Update{{ PrefixName }}Input
    ) -> {{ PrefixName }}Response:
        """
        Update an existing {{ prefix_name }} entity.
        
        Args:
            info: GraphQL execution info containing context
            id: ID of the {{ prefix_name }} to update
            input: Input data for updating the {{ prefix_name }}
            
        Returns:
            {{ PrefixName }}Response with the updated entity or error information
        """
        context: ResolverContext = info.context
        
        try:
            # Validate input has some updates
            if not input.has_updates():
                return {{ PrefixName }}Response(
                    success=False,
                    message="No updates provided",
                    {{ prefix_name }}=None
                )
            
            # Convert string ID to UUID
            try:
                entity_uuid = uuid.UUID(str(id))
            except ValueError:
                return {{ PrefixName }}Response(
                    success=False,
                    message="Invalid ID format",
                    {{ prefix_name }}=None
                )
            
            # Check if entity exists
            existing_entity = await context.{{ prefix_name }}_repository.get_by_id(entity_uuid)
            if not existing_entity:
                return {{ PrefixName }}Response(
                    success=False,
                    message=f"{{ PrefixName }} with ID '{id}' not found",
                    {{ prefix_name }}=None
                )
            
            # Validate input data
            validation_result = await self._validate_update_input(input, existing_entity, context)
            if not validation_result["is_valid"]:
                return {{ PrefixName }}Response(
                    success=False,
                    message="Validation failed",
                    {{ prefix_name }}=None
                )
            
            # Check for name conflicts (if name is being updated)
            if input.name and input.name != existing_entity.name:
                name_conflict = await context.{{ prefix_name }}_repository.get_by_name(input.name)
                if name_conflict and name_conflict.id != entity_uuid:
                    return {{ PrefixName }}Response(
                        success=False,
                        message=f"{{ PrefixName }} with name '{input.name}' already exists",
                        {{ prefix_name }}=None
                    )
            
            # Prepare update data
            update_data = {}
            if input.name is not None:
                update_data['name'] = input.name
            
            # Perform the update
            updated_entity = await context.{{ prefix_name }}_repository.update(entity_uuid, **update_data)
            
            if not updated_entity:
                return {{ PrefixName }}Response(
                    success=False,
                    message="Failed to update {{ prefix_name }}",
                    {{ prefix_name }}=None
                )
            
            # Clear DataLoader caches
            context.{{ prefix_name }}_loader.clear_by_id(str(entity_uuid))
            context.{{ prefix_name }}_loader.clear_by_name(existing_entity.name)
            if input.name and input.name != existing_entity.name:
                context.{{ prefix_name }}_loader.clear_by_name(input.name)
            
            # Convert to GraphQL type
            graphql_type = self._entity_to_graphql_type(updated_entity)
            
            return {{ PrefixName }}Response(
                success=True,
                message=f"{{ PrefixName }} updated successfully",
                {{ prefix_name }}=graphql_type
            )
            
        except IntegrityError as e:
            await context.session.rollback()
            return {{ PrefixName }}Response(
                success=False,
                message="Update would violate data integrity constraints",
                {{ prefix_name }}=None
            )
        except SQLAlchemyError as e:
            await context.session.rollback()
            print(f"Database error updating {{ prefix_name }}: {e}")
            return {{ PrefixName }}Response(
                success=False,
                message="Database error occurred while updating {{ prefix_name }}",
                {{ prefix_name }}=None
            )
        except Exception as e:
            await context.session.rollback()
            print(f"Unexpected error updating {{ prefix_name }}: {e}")
            return {{ PrefixName }}Response(
                success=False,
                message="An unexpected error occurred",
                {{ prefix_name }}=None
            )
    
    @strawberry.mutation(description="Delete a {{ prefix_name }}")
    async def delete_{{ prefix_name }}(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        confirm: bool = False
    ) -> Delete{{ PrefixName }}Response:
        """
        Delete a {{ prefix_name }} entity.
        
        Args:
            info: GraphQL execution info containing context
            id: ID of the {{ prefix_name }} to delete
            confirm: Confirmation flag to prevent accidental deletions
            
        Returns:
            Delete{{ PrefixName }}Response with deletion confirmation or error information
        """
        context: ResolverContext = info.context
        
        try:
            # Require confirmation
            if not confirm:
                return Delete{{ PrefixName }}Response(
                    success=False,
                    message="Deletion must be confirmed by setting confirm=true",
                    deleted_id=None
                )
            
            # Convert string ID to UUID
            try:
                entity_uuid = uuid.UUID(str(id))
            except ValueError:
                return Delete{{ PrefixName }}Response(
                    success=False,
                    message="Invalid ID format",
                    deleted_id=None
                )
            
            # Check if entity exists
            existing_entity = await context.{{ prefix_name }}_repository.get_by_id(entity_uuid)
            if not existing_entity:
                return Delete{{ PrefixName }}Response(
                    success=False,
                    message=f"{{ PrefixName }} with ID '{id}' not found",
                    deleted_id=None
                )
            
            # Check if entity can be deleted (business rules)
            can_delete = await self._can_delete_entity(existing_entity, context)
            if not can_delete["allowed"]:
                return Delete{{ PrefixName }}Response(
                    success=False,
                    message=can_delete["reason"],
                    deleted_id=None
                )
            
            # Store name for cache clearing
            entity_name = existing_entity.name
            
            # Perform the deletion
            deleted = await context.{{ prefix_name }}_repository.delete(entity_uuid)
            
            if not deleted:
                return Delete{{ PrefixName }}Response(
                    success=False,
                    message="Failed to delete {{ prefix_name }}",
                    deleted_id=None
                )
            
            # Clear DataLoader caches
            context.{{ prefix_name }}_loader.clear_by_id(str(entity_uuid))
            context.{{ prefix_name }}_loader.clear_by_name(entity_name)
            
            return Delete{{ PrefixName }}Response(
                success=True,
                message=f"{{ PrefixName }} '{entity_name}' deleted successfully",
                deleted_id=str(entity_uuid)
            )
            
        except SQLAlchemyError as e:
            await context.session.rollback()
            print(f"Database error deleting {{ prefix_name }}: {e}")
            return Delete{{ PrefixName }}Response(
                success=False,
                message="Database error occurred while deleting {{ prefix_name }}",
                deleted_id=None
            )
        except Exception as e:
            await context.session.rollback()
            print(f"Unexpected error deleting {{ prefix_name }}: {e}")
            return Delete{{ PrefixName }}Response(
                success=False,
                message="An unexpected error occurred",
                deleted_id=None
            )
    
    @strawberry.mutation(description="Create multiple {{ prefix_name }}s in a batch")
    async def create_multiple_{{ prefix_name }}s(
        self,
        info: strawberry.Info,
        input: CreateMultiple{{ PrefixName }}Input
    ) -> List[{{ PrefixName }}Response]:
        """
        Create multiple {{ prefix_name }} entities in a single operation.
        
        Args:
            info: GraphQL execution info containing context
            input: Input data for creating multiple {{ prefix_name }}s
            
        Returns:
            List of {{ PrefixName }}Response objects for each creation attempt
        """
        context: ResolverContext = info.context
        results = []
        
        try:
            # Process each entity creation
            for create_input in input.{{ prefix_name }}s:
                try:
                    # Validate individual input
                    validation_result = await self._validate_create_input(create_input, context)
                    if not validation_result["is_valid"]:
                        results.append({{ PrefixName }}Response(
                            success=False,
                            message=f"Validation failed for '{create_input.name}'",
                            {{ prefix_name }}=None
                        ))
                        if not input.skip_validation_errors:
                            break
                        continue
                    
                    # Check for duplicates
                    existing = await context.{{ prefix_name }}_repository.get_by_name(create_input.name)
                    if existing:
                        results.append({{ PrefixName }}Response(
                            success=False,
                            message=f"{{ PrefixName }} with name '{create_input.name}' already exists",
                            {{ prefix_name }}=None
                        ))
                        if not input.skip_validation_errors:
                            break
                        continue
                    
                    # Create entity
                    entity_data = self._input_to_entity_data(create_input)
                    created_entity = await context.{{ prefix_name }}_repository.create(**entity_data)
                    
                    # Convert to GraphQL type
                    graphql_type = self._entity_to_graphql_type(created_entity)
                    
                    results.append({{ PrefixName }}Response(
                        success=True,
                        message=f"{{ PrefixName }} '{create_input.name}' created successfully",
                        {{ prefix_name }}=graphql_type
                    ))
                    
                except Exception as e:
                    results.append({{ PrefixName }}Response(
                        success=False,
                        message=f"Error creating '{create_input.name}': {str(e)}",
                        {{ prefix_name }}=None
                    ))
                    if not input.skip_validation_errors:
                        break
            
            # Clear all DataLoader caches after batch operation
            context.{{ prefix_name }}_loader.clear_all()
            
            return results
            
        except Exception as e:
            await context.session.rollback()
            print(f"Batch creation error: {e}")
            return [{{ PrefixName }}Response(
                success=False,
                message="Batch operation failed",
                {{ prefix_name }}=None
            )]
    
    # Helper methods
    
    async def _validate_create_input(
        self, 
        input: Create{{ PrefixName }}Input, 
        context: ResolverContext
    ) -> Dict[str, Any]:
        """
        Validate input for creating a {{ prefix_name }}.
        
        Args:
            input: Create input data
            context: Resolver context
            
        Returns:
            Dictionary with validation result
        """
        # Basic validation
        if not input.name or len(input.name.strip()) == 0:
            return {"is_valid": False, "errors": ["Name is required"]}
        
        if len(input.name) > 255:
            return {"is_valid": False, "errors": ["Name must be 255 characters or less"]}
        
        # Use validation service if available
        if VALIDATION_SERVICE_AVAILABLE:
            # Additional business rule validation would go here
            pass
        
        return {"is_valid": True, "errors": []}
    
    async def _validate_update_input(
        self, 
        input: Update{{ PrefixName }}Input, 
        existing_entity: {{ PrefixName }}Entity,
        context: ResolverContext
    ) -> Dict[str, Any]:
        """
        Validate input for updating a {{ prefix_name }}.
        
        Args:
            input: Update input data
            existing_entity: The existing entity being updated
            context: Resolver context
            
        Returns:
            Dictionary with validation result
        """
        # Basic validation
        if input.name is not None:
            if len(input.name.strip()) == 0:
                return {"is_valid": False, "errors": ["Name cannot be empty"]}
            
            if len(input.name) > 255:
                return {"is_valid": False, "errors": ["Name must be 255 characters or less"]}
        
        # Use validation service if available
        if VALIDATION_SERVICE_AVAILABLE:
            # Additional business rule validation would go here
            pass
        
        return {"is_valid": True, "errors": []}
    
    async def _can_delete_entity(
        self, 
        entity: {{ PrefixName }}Entity, 
        context: ResolverContext
    ) -> Dict[str, Any]:
        """
        Check if an entity can be deleted based on business rules.
        
        Args:
            entity: The entity to check for deletion
            context: Resolver context
            
        Returns:
            Dictionary with deletion permission and reason
        """
        # Basic checks - can be extended with business rules
        
        # Example: Check if entity is in use elsewhere
        # This would typically involve checking foreign key relationships
        # For now, we'll allow all deletions
        
        return {"allowed": True, "reason": None}
    
    def _input_to_entity_data(self, input: Create{{ PrefixName }}Input) -> Dict[str, Any]:
        """
        Convert create input to entity data dictionary.
        
        Args:
            input: Create input data
            
        Returns:
            Dictionary of entity data for repository creation
        """
        return {
            "name": input.name.strip(),
            "status": "ACTIVE"  # Default status
        }
    
    def _entity_to_graphql_type(self, entity: {{ PrefixName }}Entity):
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


# Create resolver instance for use in schema
{{ prefix_name }}_mutation_resolver = {{ PrefixName }}MutationResolver() 