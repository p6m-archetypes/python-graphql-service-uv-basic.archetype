"""
Utility functions for converting between Pydantic models and Strawberry GraphQL types.

This module provides utilities to transform existing Pydantic models into
Strawberry GraphQL types while preserving validation logic and field descriptions.
"""

from typing import Any, Dict, Optional, Type, TypeVar, get_type_hints, Union
import strawberry
from pydantic import BaseModel
from datetime import datetime
import uuid

# Type variables for generic conversion utilities
PydanticModel = TypeVar('PydanticModel', bound=BaseModel)


def convert_pydantic_field_type(field_type: Type, is_optional: bool = False) -> Type:
    """
    Convert a Pydantic field type to its Strawberry equivalent.
    
    Args:
        field_type: The Pydantic field type
        is_optional: Whether the field is optional
        
    Returns:
        The equivalent Strawberry type
    """
    # Handle basic types
    type_mapping = {
        str: str,
        int: int,
        float: float,
        bool: bool,
        datetime: datetime,
        uuid.UUID: strawberry.ID,
    }
    
    # Handle Optional types
    if hasattr(field_type, '__origin__'):
        if field_type.__origin__ is Union:
            # Handle Optional[T] which is Union[T, None]
            args = field_type.__args__
            if len(args) == 2 and type(None) in args:
                non_none_type = next(arg for arg in args if arg is not type(None))
                return Optional[convert_pydantic_field_type(non_none_type, True)]
        elif field_type.__origin__ is list:
            # Handle List[T]
            inner_type = field_type.__args__[0]
            converted_inner = convert_pydantic_field_type(inner_type)
            return list[converted_inner] if not is_optional else Optional[list[converted_inner]]
    
    # Direct mapping for simple types
    converted = type_mapping.get(field_type, field_type)
    
    return Optional[converted] if is_optional else converted


def extract_field_info(pydantic_model: Type[PydanticModel], field_name: str) -> Dict[str, Any]:
    """
    Extract field information from a Pydantic model.
    
    Args:
        pydantic_model: The Pydantic model class
        field_name: Name of the field to extract info for
        
    Returns:
        Dictionary containing field information
    """
    field_info = {
        'description': None,
        'default': None,
        'is_optional': False,
        'type': str  # fallback
    }
    
    # Get field from model
    if hasattr(pydantic_model, '__fields__'):
        model_field = pydantic_model.__fields__.get(field_name)
        if model_field:
            field_info['description'] = model_field.field_info.description
            field_info['default'] = model_field.default
            field_info['is_optional'] = not model_field.required
            
            # Get type information
            type_hints = get_type_hints(pydantic_model)
            if field_name in type_hints:
                field_info['type'] = convert_pydantic_field_type(
                    type_hints[field_name], 
                    field_info['is_optional']
                )
    
    return field_info


def pydantic_to_strawberry_type(
    pydantic_model: Type[PydanticModel],
    type_name: Optional[str] = None,
    description: Optional[str] = None,
    exclude_fields: Optional[list[str]] = None
) -> Type:
    """
    Convert a Pydantic model to a Strawberry GraphQL type.
    
    Args:
        pydantic_model: The Pydantic model to convert
        type_name: Override the generated type name
        description: Override the type description
        exclude_fields: List of field names to exclude from the GraphQL type
        
    Returns:
        A Strawberry GraphQL type class
    """
    exclude_fields = exclude_fields or []
    
    # Generate type name if not provided
    if not type_name:
        type_name = f"{pydantic_model.__name__.replace('Dto', '').replace('Model', '')}Type"
    
    # Use model docstring as description if not provided
    if not description:
        description = pydantic_model.__doc__ or f"GraphQL type for {pydantic_model.__name__}"
    
    # Create a dictionary to hold the type fields
    type_fields = {}
    
    # Extract fields from the Pydantic model
    if hasattr(pydantic_model, '__fields__'):
        for field_name, model_field in pydantic_model.__fields__.items():
            if field_name in exclude_fields:
                continue
                
            field_info = extract_field_info(pydantic_model, field_name)
            
            # Create Strawberry field
            type_fields[field_name] = strawberry.field(
                description=field_info['description'] or f"{field_name} field"
            )
    
    # Create the Strawberry type class dynamically
    @strawberry.type(description=description)
    class GeneratedType:
        pass
    
    # Add fields to the class
    for field_name, field_descriptor in type_fields.items():
        field_info = extract_field_info(pydantic_model, field_name)
        setattr(GeneratedType, field_name, field_descriptor)
        
        # Add type annotation
        if hasattr(GeneratedType, '__annotations__'):
            GeneratedType.__annotations__[field_name] = field_info['type']
        else:
            GeneratedType.__annotations__ = {field_name: field_info['type']}
    
    # Set the class name
    GeneratedType.__name__ = type_name
    GeneratedType.__qualname__ = type_name
    
    return GeneratedType


def create_strawberry_from_pydantic(
    pydantic_instance: PydanticModel,
    strawberry_type: Type,
    field_mapping: Optional[Dict[str, str]] = None
) -> Any:
    """
    Create a Strawberry type instance from a Pydantic model instance.
    
    Args:
        pydantic_instance: Instance of a Pydantic model
        strawberry_type: The target Strawberry type class
        field_mapping: Optional mapping of field names (pydantic -> strawberry)
        
    Returns:
        Instance of the Strawberry type
    """
    field_mapping = field_mapping or {}
    
    # Get the data from the Pydantic instance
    data = pydantic_instance.dict() if hasattr(pydantic_instance, 'dict') else pydantic_instance.__dict__
    
    # Map field names if necessary
    mapped_data = {}
    for pydantic_field, value in data.items():
        strawberry_field = field_mapping.get(pydantic_field, pydantic_field)
        mapped_data[strawberry_field] = value
    
    # Create the Strawberry type instance
    return strawberry_type(**mapped_data)


def create_pydantic_from_strawberry(
    strawberry_instance: Any,
    pydantic_type: Type[PydanticModel],
    field_mapping: Optional[Dict[str, str]] = None
) -> PydanticModel:
    """
    Create a Pydantic model instance from a Strawberry type instance.
    
    Args:
        strawberry_instance: Instance of a Strawberry type
        pydantic_type: The target Pydantic model class
        field_mapping: Optional mapping of field names (strawberry -> pydantic)
        
    Returns:
        Instance of the Pydantic model
    """
    field_mapping = field_mapping or {}
    
    # Extract data from Strawberry instance
    data = {}
    for field_name in strawberry_instance.__dataclass_fields__:
        if hasattr(strawberry_instance, field_name):
            value = getattr(strawberry_instance, field_name)
            pydantic_field = field_mapping.get(field_name, field_name)
            data[pydantic_field] = value
    
    # Create the Pydantic instance
    return pydantic_type(**data) 