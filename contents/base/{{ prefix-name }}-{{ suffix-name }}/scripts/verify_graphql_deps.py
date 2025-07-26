#!/usr/bin/env python3
"""
Verification script for Strawberry GraphQL dependencies.
This script tests that all GraphQL-related dependencies are properly installed
and compatible with each other.
"""

import sys
from typing import Optional


def test_strawberry_import():
    """Test that Strawberry GraphQL can be imported."""
    try:
        import strawberry
        print(f"✅ Strawberry GraphQL imported successfully (version: {strawberry.__version__})")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Strawberry GraphQL: {e}")
        return False


def test_fastapi_integration():
    """Test that Strawberry FastAPI integration works."""
    try:
        from strawberry.fastapi import GraphQLRouter
        print("✅ Strawberry FastAPI integration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Strawberry FastAPI integration: {e}")
        return False


def test_basic_schema_creation():
    """Test creating a basic GraphQL schema."""
    try:
        import strawberry
        
        @strawberry.type
        class Query:
            @strawberry.field
            def hello(self) -> str:
                return "Hello, GraphQL!"
        
        schema = strawberry.Schema(query=Query)
        print("✅ Basic GraphQL schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create basic GraphQL schema: {e}")
        return False


def test_version_compatibility():
    """Test that versions meet our requirements."""
    try:
        import strawberry
        from packaging import version
        
        strawberry_version = version.parse(strawberry.__version__)
        required_version = version.parse("0.258.0")
        
        if strawberry_version >= required_version:
            print(f"✅ Strawberry version {strawberry_version} meets requirement (>= {required_version})")
            return True
        else:
            print(f"❌ Strawberry version {strawberry_version} below requirement (>= {required_version})")
            return False
    except Exception as e:
        print(f"❌ Failed to verify version compatibility: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🔍 Verifying Strawberry GraphQL dependencies...")
    print("=" * 50)
    
    tests = [
        test_strawberry_import,
        test_fastapi_integration,
        test_basic_schema_creation,
        test_version_compatibility,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    if success_count == total_count:
        print(f"🎉 All {total_count} tests passed! GraphQL dependencies are ready.")
        return 0
    else:
        print(f"❌ {total_count - success_count} out of {total_count} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 