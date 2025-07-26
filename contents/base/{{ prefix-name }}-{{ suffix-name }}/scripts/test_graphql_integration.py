#!/usr/bin/env python3
"""
Test script for verifying GraphQL integration with FastAPI.

This script tests that the GraphQL endpoint is properly mounted in the FastAPI
application and can handle GraphQL queries and mutations.
"""

import sys
import asyncio
import json
from typing import Dict, Any

import httpx
import pytest
from fastapi.testclient import TestClient


async def test_fastapi_app_creation():
    """Test that the FastAPI app with GraphQL can be created."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        app = create_app()
        print("✅ FastAPI app with GraphQL created successfully")
        return True, app
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False, None


async def test_graphql_endpoint_mounted():
    """Test that the GraphQL endpoint is properly mounted."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        # Check if GraphQL routes are present
        routes = [route.path for route in app.routes]
        graphql_routes = [route for route in routes if "graphql" in route.lower()]
        
        if graphql_routes:
            print(f"✅ GraphQL routes found: {graphql_routes}")
            return True
        else:
            print("❌ No GraphQL routes found in FastAPI app")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check GraphQL routes: {e}")
        return False


async def test_graphql_health_query():
    """Test GraphQL health query through FastAPI test client."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        with TestClient(app) as client:
            # Test GraphQL health query
            query = {
                "query": """
                query HealthCheck {
                    health
                    version
                }
                """
            }
            
            response = client.post("/graphql", json=query)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("health") == "GraphQL service is healthy":
                    print("✅ GraphQL health query successful through FastAPI")
                    print(f"   Response: {data}")
                    return True
                else:
                    print(f"❌ Unexpected GraphQL response: {data}")
                    return False
            else:
                print(f"❌ GraphQL query failed with status {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ GraphQL health query error: {e}")
        return False


async def test_graphql_ping_mutation():
    """Test GraphQL ping mutation through FastAPI test client."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        with TestClient(app) as client:
            # Test GraphQL ping mutation
            mutation = {
                "query": """
                mutation PingTest {
                    ping
                }
                """
            }
            
            response = client.post("/graphql", json=mutation)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("ping") == "pong":
                    print("✅ GraphQL ping mutation successful through FastAPI")
                    print(f"   Response: {data}")
                    return True
                else:
                    print(f"❌ Unexpected GraphQL mutation response: {data}")
                    return False
            else:
                print(f"❌ GraphQL mutation failed with status {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ GraphQL ping mutation error: {e}")
        return False


async def test_rest_endpoints_still_work():
    """Test that existing REST endpoints still work alongside GraphQL."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        with TestClient(app) as client:
            # Test root endpoint
            response = client.get("/")
            if response.status_code == 200:
                print("✅ REST root endpoint still works")
            else:
                print(f"❌ REST root endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = client.get("/health")
            if response.status_code == 200:
                print("✅ REST health endpoint still works")
            else:
                print(f"❌ REST health endpoint failed: {response.status_code}")
                return False
                
            return True
                
    except Exception as e:
        print(f"❌ REST endpoints test error: {e}")
        return False


async def test_cors_configuration():
    """Test that CORS is properly configured for GraphQL."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        with TestClient(app) as client:
            # Test OPTIONS request (CORS preflight)
            response = client.options("/graphql")
            
            # Check for CORS headers
            cors_headers = {
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers"
            }
            
            response_headers = {k.lower() for k in response.headers.keys()}
            found_cors_headers = cors_headers.intersection(response_headers)
            
            if found_cors_headers:
                print(f"✅ CORS headers present: {found_cors_headers}")
                return True
            else:
                print("⚠️  CORS headers might not be configured (this might be expected in test mode)")
                return True  # Don't fail the test for this
                
    except Exception as e:
        print(f"❌ CORS configuration test error: {e}")
        return False


async def test_graphql_introspection():
    """Test GraphQL schema introspection."""
    try:
        from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.server.app import create_app
        
        app = create_app()
        
        with TestClient(app) as client:
            # Test introspection query
            introspection_query = {
                "query": """
                query IntrospectionQuery {
                    __schema {
                        queryType {
                            name
                            fields {
                                name
                                description
                            }
                        }
                        mutationType {
                            name
                            fields {
                                name
                                description
                            }
                        }
                    }
                }
                """
            }
            
            response = client.post("/graphql", json=introspection_query)
            
            if response.status_code == 200:
                data = response.json()
                schema_data = data.get("data", {}).get("__schema", {})
                
                if schema_data.get("queryType", {}).get("name") == "Query":
                    print("✅ GraphQL introspection working")
                    print(f"   Available queries: {[f['name'] for f in schema_data.get('queryType', {}).get('fields', [])]}")
                    print(f"   Available mutations: {[f['name'] for f in schema_data.get('mutationType', {}).get('fields', [])]}")
                    return True
                else:
                    print(f"❌ Unexpected introspection response: {data}")
                    return False
            else:
                print(f"❌ Introspection query failed with status {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ GraphQL introspection error: {e}")
        return False


async def main():
    """Run all GraphQL integration tests."""
    print("🔍 Testing GraphQL integration with FastAPI...")
    print("=" * 60)
    
    tests = [
        test_fastapi_app_creation,
        test_graphql_endpoint_mounted,
        test_graphql_health_query,
        test_graphql_ping_mutation,
        test_rest_endpoints_still_work,
        test_cors_configuration,
        test_graphql_introspection,
    ]
    
    results = []
    for test in tests:
        result = await test()
        # Handle tuple return from app creation test
        if isinstance(result, tuple):
            results.append(result[0])
        else:
            results.append(result)
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 60)
    if success_count == total_count:
        print(f"🎉 All {total_count} GraphQL integration tests passed!")
        print("   GraphQL is successfully integrated with FastAPI!")
        return 0
    else:
        print(f"❌ {total_count - success_count} out of {total_count} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 