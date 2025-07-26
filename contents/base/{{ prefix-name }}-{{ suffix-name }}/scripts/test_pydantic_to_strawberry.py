#!/usr/bin/env python3
"""
Test script for verifying Pydantic to Strawberry type transformations.

This script tests the conversion utilities and validates that all GraphQL types
work correctly with the existing Pydantic models.
"""

import sys
import asyncio
from typing import List

# Mock strawberry for testing if not available
try:
    import strawberry
    STRAWBERRY_AVAILABLE = True
except ImportError:
    STRAWBERRY_AVAILABLE = False
    print("⚠️  Strawberry GraphQL not available - using mock for testing")


async def test_imports():
    """Test that all GraphQL types can be imported."""
    try:
        # Test entity types
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            {{ PrefixName }}Type,
            {{ PrefixName }}Response,
            Delete{{ PrefixName }}Response,
            example_dto_to_graphql,
            graphql_to_example_dto
        )
        
        # Test connection types
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            PageInfo,
            {{ PrefixName }}Edge,
            {{ PrefixName }}Connection,
            {{ PrefixName }}ConnectionArgs,
            encode_cursor,
            decode_cursor,
            page_result_to_connection,
            create_empty_connection
        )
        
        # Test input types
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.inputs import (
            Create{{ PrefixName }}Input,
            Update{{ PrefixName }}Input,
            {{ PrefixName }}Filter,
            {{ PrefixName }}Sort,
            SortDirection
        )
        
        # Test utilities
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            convert_pydantic_field_type,
            extract_field_info,
            pydantic_to_strawberry_type,
            create_strawberry_from_pydantic,
            create_pydantic_from_strawberry
        )
        
        print("✅ All GraphQL types imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import GraphQL types: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing types: {e}")
        return False


async def test_pydantic_to_graphql_conversion():
    """Test conversion from Pydantic models to GraphQL types."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            example_dto_to_graphql,
            {{ PrefixName }}Type
        )
        
        # Create a test Pydantic instance
        example_dto = ExampleDto(
            id="test-123",
            name="Test Example"
        )
        
        # Convert to GraphQL type
        graphql_type = example_dto_to_graphql(example_dto)
        
        # Validate conversion
        if graphql_type.id == example_dto.id and graphql_type.name == example_dto.name:
            print("✅ Pydantic to GraphQL conversion working")
            return True
        else:
            print(f"❌ Conversion failed: {graphql_type.id} != {example_dto.id} or {graphql_type.name} != {example_dto.name}")
            return False
            
    except Exception as e:
        print(f"❌ Pydantic to GraphQL conversion error: {e}")
        return False


async def test_graphql_to_pydantic_conversion():
    """Test conversion from GraphQL types to Pydantic models."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            {{ PrefixName }}Type,
            graphql_to_example_dto
        )
        
        # Create a test GraphQL type instance
        if STRAWBERRY_AVAILABLE:
            graphql_type = {{ PrefixName }}Type(
                id="test-456",
                name="Test GraphQL"
            )
        else:
            # Mock for testing
            class MockGraphQLType:
                def __init__(self, id, name):
                    self.id = id
                    self.name = name
            graphql_type = MockGraphQLType("test-456", "Test GraphQL")
        
        # Convert to Pydantic type
        example_dto = graphql_to_example_dto(graphql_type)
        
        # Validate conversion
        if example_dto.id == graphql_type.id and example_dto.name == graphql_type.name:
            print("✅ GraphQL to Pydantic conversion working")
            return True
        else:
            print(f"❌ Conversion failed: {example_dto.id} != {graphql_type.id} or {example_dto.name} != {graphql_type.name}")
            return False
            
    except Exception as e:
        print(f"❌ GraphQL to Pydantic conversion error: {e}")
        return False


async def test_cursor_utilities():
    """Test cursor encoding and decoding utilities."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            encode_cursor,
            decode_cursor
        )
        
        # Test encoding and decoding
        original_value = "test-id-123"
        encoded_cursor = encode_cursor(original_value)
        decoded_value = decode_cursor(encoded_cursor)
        
        if decoded_value == original_value:
            print("✅ Cursor encoding/decoding working")
            print(f"   Original: {original_value}")
            print(f"   Encoded: {encoded_cursor}")
            print(f"   Decoded: {decoded_value}")
            return True
        else:
            print(f"❌ Cursor encoding/decoding failed: {decoded_value} != {original_value}")
            return False
            
    except Exception as e:
        print(f"❌ Cursor utilities error: {e}")
        return False


async def test_connection_creation():
    """Test GraphQL connection creation from PageResult."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.models.pagination import PageResult
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            {{ PrefixName }}Type,
            page_result_to_connection,
            create_empty_connection
        )
        
        # Create mock {{ PrefixName }}Type instances
        if STRAWBERRY_AVAILABLE:
            mock_items = [
                {{ PrefixName }}Type(id="1", name="First"),
                {{ PrefixName }}Type(id="2", name="Second"),
                {{ PrefixName }}Type(id="3", name="Third")
            ]
        else:
            # Mock for testing
            class MockType:
                def __init__(self, id, name):
                    self.id = id
                    self.name = name
            mock_items = [
                MockType("1", "First"),
                MockType("2", "Second"), 
                MockType("3", "Third")
            ]
        
        # Create a PageResult
        page_result = PageResult.create(
            items=mock_items,
            total_elements=10,
            page=0,
            size=3
        )
        
        # Convert to GraphQL connection
        connection = page_result_to_connection(page_result)
        
        # Validate connection
        if (len(connection.edges) == 3 and 
            connection.total_count == 10 and
            connection.page_info.has_next_page == True):
            print("✅ Connection creation from PageResult working")
            print(f"   Edges: {len(connection.edges)}")
            print(f"   Total count: {connection.total_count}")
            print(f"   Has next: {connection.page_info.has_next_page}")
            return True
        else:
            print(f"❌ Connection creation failed")
            return False
    
    except Exception as e:
        print(f"❌ Connection creation error: {e}")
        return False


async def test_empty_connection():
    """Test empty connection creation."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
            create_empty_connection
        )
        
        # Create empty connection
        empty_connection = create_empty_connection()
        
        # Validate empty connection
        if (len(empty_connection.edges) == 0 and
            empty_connection.total_count == 0 and
            empty_connection.page_info.has_next_page == False and
            empty_connection.page_info.has_previous_page == False):
            print("✅ Empty connection creation working")
            return True
        else:
            print(f"❌ Empty connection creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Empty connection creation error: {e}")
        return False


async def test_input_types():
    """Test GraphQL input type functionality."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.inputs import (
            Create{{ PrefixName }}Input,
            Update{{ PrefixName }}Input,
            {{ PrefixName }}Filter,
            SortDirection
        )
        
        # Test Create input
        if STRAWBERRY_AVAILABLE:
            create_input = Create{{ PrefixName }}Input(name="Test Create")
        else:
            # Mock for testing
            class MockCreateInput:
                def __init__(self, name):
                    self.name = name
                def to_example_dto(self):
                    from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import ExampleDto
                    return ExampleDto(id=None, name=self.name)
            create_input = MockCreateInput("Test Create")
        
        example_dto = create_input.to_example_dto()
        if example_dto.name == "Test Create":
            print("✅ Create input type working")
        else:
            print("❌ Create input type failed")
            return False
        
        # Test Update input
        if STRAWBERRY_AVAILABLE:
            update_input = Update{{ PrefixName }}Input(name="Updated Name")
        else:
            class MockUpdateInput:
                def __init__(self, name):
                    self.name = name
                def has_updates(self):
                    return self.name is not None
            update_input = MockUpdateInput("Updated Name")
        
        if update_input.has_updates():
            print("✅ Update input type working")
        else:
            print("❌ Update input type failed")
            return False
        
        # Test Filter input
        if STRAWBERRY_AVAILABLE:
            filter_input = {{ PrefixName }}Filter(name_contains="test")
        else:
            class MockFilter:
                def __init__(self, name_contains=None):
                    self.name_contains = name_contains
                    self.name = None
                    self.name_starts_with = None
                    self.name_ends_with = None
                    self.ids = None
                    self.exclude_ids = None
                    self.AND = None
                    self.OR = None
                    self.NOT = None
                def has_filters(self):
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
            filter_input = MockFilter(name_contains="test")
        
        if filter_input.has_filters():
            print("✅ Filter input type working")
            return True
        else:
            print("❌ Filter input type failed")
            return False
            
    except Exception as e:
        print(f"❌ Input types test error: {e}")
        return False


async def main():
    """Run all type transformation tests."""
    print("🔍 Testing Pydantic to Strawberry type transformations...")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_pydantic_to_graphql_conversion,
        test_graphql_to_pydantic_conversion,
        test_cursor_utilities,
        test_connection_creation,
        test_empty_connection,
        test_input_types,
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 70)
    if success_count == total_count:
        print(f"🎉 All {total_count} type transformation tests passed!")
        print("   Pydantic models successfully converted to Strawberry GraphQL types!")
        return 0
    else:
        print(f"❌ {total_count - success_count} out of {total_count} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 