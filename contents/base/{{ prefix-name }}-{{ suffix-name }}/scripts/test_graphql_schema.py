#!/usr/bin/env python3
"""
Test script for verifying basic GraphQL schema functionality.

This script tests that the GraphQL schema can be created, introspected,
and executed with basic queries and mutations.
"""

import sys
import asyncio
from typing import Dict, Any


async def test_schema_creation():
    """Test that the GraphQL schema can be created successfully."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema
        print("✅ GraphQL schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create GraphQL schema: {e}")
        return False


async def test_schema_introspection():
    """Test that schema introspection works correctly."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema
        
        # Test basic introspection query
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType {
                    name
                }
                mutationType {
                    name
                }
            }
        }
        """
        
        result = await schema.execute(introspection_query)
        
        if result.errors:
            print(f"❌ Schema introspection failed: {result.errors}")
            return False
            
        data = result.data
        if (data and 
            data.get("__schema", {}).get("queryType", {}).get("name") == "Query" and
            data.get("__schema", {}).get("mutationType", {}).get("name") == "Mutation"):
            print("✅ Schema introspection successful")
            return True
        else:
            print(f"❌ Unexpected introspection result: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Schema introspection error: {e}")
        return False


async def test_health_query():
    """Test the health check query."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema
        
        query = """
        query HealthCheck {
            health
        }
        """
        
        result = await schema.execute(query)
        
        if result.errors:
            print(f"❌ Health query failed: {result.errors}")
            return False
            
        if result.data and result.data.get("health") == "GraphQL service is healthy":
            print("✅ Health query successful")
            return True
        else:
            print(f"❌ Unexpected health query result: {result.data}")
            return False
            
    except Exception as e:
        print(f"❌ Health query error: {e}")
        return False


async def test_version_query():
    """Test the version query."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema
        
        query = """
        query VersionCheck {
            version
        }
        """
        
        result = await schema.execute(query)
        
        if result.errors:
            print(f"❌ Version query failed: {result.errors}")
            return False
            
        if result.data and result.data.get("version") == "0.1.0":
            print("✅ Version query successful")
            return True
        else:
            print(f"❌ Unexpected version query result: {result.data}")
            return False
            
    except Exception as e:
        print(f"❌ Version query error: {e}")
        return False


async def test_ping_mutation():
    """Test the ping mutation."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema
        
        mutation = """
        mutation PingTest {
            ping
        }
        """
        
        result = await schema.execute(mutation)
        
        if result.errors:
            print(f"❌ Ping mutation failed: {result.errors}")
            return False
            
        if result.data and result.data.get("ping") == "pong":
            print("✅ Ping mutation successful")
            return True
        else:
            print(f"❌ Unexpected ping mutation result: {result.data}")
            return False
            
    except Exception as e:
        print(f"❌ Ping mutation error: {e}")
        return False


async def main():
    """Run all GraphQL schema tests."""
    print("🔍 Testing GraphQL schema functionality...")
    print("=" * 50)
    
    tests = [
        test_schema_creation,
        test_schema_introspection,
        test_health_query,
        test_version_query,
        test_ping_mutation,
    ]
    
    results = []
    for test in tests:
        results.append(await test())
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    if success_count == total_count:
        print(f"🎉 All {total_count} GraphQL schema tests passed!")
        return 0
    else:
        print(f"❌ {total_count - success_count} out of {total_count} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 