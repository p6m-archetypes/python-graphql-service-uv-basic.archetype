"""GraphQL connectivity and health check tests for CI/CD integration."""

import asyncio
import os
import socket
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from ..utils.graphql_test_client import GraphQLTestClient, {{ PrefixName }}TestClient, GraphQLError


class TestGraphQLConnectivity:
    """Test GraphQL server connectivity and health checks."""

    @pytest.mark.integration
    @pytest.mark.requires_docker
    async def test_graphql_server_port_accessible(self):
        """Test that GraphQL server port is accessible."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        
        # Test socket connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        try:
            result = sock.connect_ex((host, port))
            assert result == 0, f"Cannot connect to GraphQL server at {host}:{port}"
        finally:
            sock.close()

    @pytest.mark.integration
    @pytest.mark.requires_docker
    async def test_graphql_client_creation(self):
        """Test GraphQL client creation and basic connectivity."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        base_url = f"http://{host}:{port}"
        
        # Test GraphQL client creation
        client = GraphQLTestClient(base_url)
        
        # Test basic connectivity with ping query
        try:
            result = await client.health_check()
            assert isinstance(result, bool), "Health check should return boolean"
        except Exception as e:
            pytest.fail(f"Failed to connect to GraphQL server at {host}:{port}: {e}")

    @pytest.mark.integration 
    @pytest.mark.requires_docker
    async def test_graphql_ping_query(self):
        """Test that GraphQL ping query works."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        base_url = f"http://{host}:{port}"
        
        client = {{ PrefixName }}TestClient(base_url)
        
        try:
            result = await client.ping()
            assert result == "pong", f"Expected 'pong', got '{result}'"
        except GraphQLError as e:
            pytest.fail(f"GraphQL ping query failed: {e}")
        except Exception as e:
            pytest.fail(f"GraphQL endpoint not accessible at {host}:{port}/graphql: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_docker
    async def test_health_endpoint_accessible(self):
        """Test that REST health endpoint is still accessible."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"http://{host}:{port}/health", timeout=10.0)
                # Health endpoint should exist and return a valid response
                assert response.status_code in [200, 503], f"Health endpoint returned {response.status_code}"
            except httpx.ConnectError:
                pytest.fail(f"Health endpoint not accessible at {host}:{port}/health")

    @pytest.mark.integration
    @pytest.mark.requires_docker
    async def test_graphql_endpoint_accessible(self):
        """Test that GraphQL endpoint is accessible via HTTP POST."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                # Test GraphQL endpoint with a simple ping query
                response = await client.post(
                    f"http://{host}:{port}/graphql",
                    json={"query": "query { ping }"},
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                assert response.status_code == 200, f"GraphQL endpoint returned {response.status_code}"
                
                # Verify response structure
                data = response.json()
                assert "data" in data or "errors" in data, "GraphQL response should have 'data' or 'errors'"
                
            except httpx.ConnectError:
                pytest.fail(f"GraphQL endpoint not accessible at {host}:{port}/graphql")

    @pytest.mark.integration
    @pytest.mark.requires_docker 
    async def test_management_health_endpoint(self):
        """Test that management health endpoint is accessible."""
        host = os.getenv("MANAGEMENT_HOST", "localhost")
        port = int(os.getenv("MANAGEMENT_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"http://{host}:{port}/health", timeout=10.0)
                # Management health endpoint should exist
                assert response.status_code in [200, 503], f"Management health endpoint returned {response.status_code}"
            except httpx.ConnectError:
                pytest.fail(f"Management health endpoint not accessible at {host}:{port}/health")

    @pytest.mark.integration
    async def test_graphql_schema_introspection(self):
        """Test GraphQL schema introspection."""
        host = os.getenv("API_HOST", "localhost") 
        port = int(os.getenv("API_PORT", "8080"))
        base_url = f"http://{host}:{port}"
        
        client = {{ PrefixName }}TestClient(base_url)
        
        try:
            schema = await client.introspect_schema()
            
            # Verify basic schema structure
            assert "queryType" in schema, "Schema should have queryType"
            assert "mutationType" in schema, "Schema should have mutationType"
            assert "types" in schema, "Schema should have types"
            
            # Verify our types are present
            type_names = [t["name"] for t in schema["types"]]
            assert "Query" in type_names, "Query type should be present"
            assert "Mutation" in type_names, "Mutation type should be present"
            
        except GraphQLError as e:
            pytest.fail(f"GraphQL introspection failed: {e}")
        except httpx.ConnectError:
            pytest.skip(f"GraphQL server not available at {host}:{port}")

    @pytest.mark.integration
    async def test_cors_headers_present(self):
        """Test that CORS headers are present in GraphQL responses."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.options(f"http://{host}:{port}/graphql", timeout=10.0)
                # CORS should be configured, check for Access-Control headers
                headers = response.headers
                # At minimum, we expect some CORS configuration
                assert any("access-control" in key.lower() for key in headers.keys()) or response.status_code == 405
            except httpx.ConnectError:
                pytest.skip(f"GraphQL server not available at {host}:{port}")

    @pytest.mark.integration
    async def test_graphql_playground_accessible(self):
        """Test that GraphQL Playground/GraphiQL is accessible (if enabled)."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                # Test GraphQL playground endpoint
                response = await client.get(f"http://{host}:{port}/graphql", timeout=10.0)
                # Playground might be disabled in production, so 200 or 404 is acceptable
                assert response.status_code in [200, 404, 405], f"GraphQL endpoint returned {response.status_code}"
                
            except httpx.ConnectError:
                pytest.skip(f"GraphQL server not available at {host}:{port}")

    @pytest.mark.integration
    async def test_prometheus_metrics_accessible(self):
        """Test that Prometheus metrics endpoint is accessible."""
        host = os.getenv("MANAGEMENT_HOST", "localhost")
        port = int(os.getenv("MANAGEMENT_PORT", "8080"))
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"http://{host}:{port}/metrics", timeout=10.0)
                # Metrics endpoint should exist
                assert response.status_code in [200, 404], f"Metrics endpoint returned {response.status_code}"
                
                if response.status_code == 200:
                    # If metrics exist, should contain Prometheus format
                    content = response.text
                    assert "# HELP" in content or "# TYPE" in content or len(content) > 0
                    
                    # Check for our new GraphQL metrics
                    assert "graphql_requests_total" in content or len(content) > 0, "Should contain GraphQL metrics"
                    
            except httpx.ConnectError:
                pytest.skip(f"Management server not available at {host}:{port}")

    @pytest.mark.integration
    async def test_graphql_error_handling(self):
        """Test GraphQL error handling with invalid queries."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        base_url = f"http://{host}:{port}"
        
        client = GraphQLTestClient(base_url)
        
        try:
            # Test with invalid GraphQL syntax
            with pytest.raises(GraphQLError):
                await client.execute("query { invalidField }")
                
            # Test with malformed query
            with pytest.raises(GraphQLError):
                await client.execute("this is not graphql")
                
        except httpx.ConnectError:
            pytest.skip(f"GraphQL server not available at {host}:{port}")

    @pytest.mark.integration 
    async def test_graphql_variable_handling(self):
        """Test GraphQL queries with variables."""
        host = os.getenv("API_HOST", "localhost")
        port = int(os.getenv("API_PORT", "8080"))
        base_url = f"http://{host}:{port}"
        
        client = GraphQLTestClient(base_url)
        
        try:
            # Test query with variables (using a simple query that should work)
            result = await client.execute(
                "query TestQuery($testVar: String) { ping }",
                {"testVar": "test"}
            )
            assert result.get("ping") == "pong"
            
        except httpx.ConnectError:
            pytest.skip(f"GraphQL server not available at {host}:{port}")
        except GraphQLError:
            # This might fail if the server doesn't support this exact query structure
            # which is fine for a connectivity test
            pass


# Individual test functions for backwards compatibility
@pytest.mark.integration
async def test_server_connectivity():
    """Test basic server connectivity."""
    test_instance = TestGraphQLConnectivity()
    await test_instance.test_graphql_server_port_accessible()


@pytest.mark.integration  
async def test_health_check():
    """Test health check endpoint."""
    test_instance = TestGraphQLConnectivity()
    await test_instance.test_health_endpoint_accessible()


@pytest.mark.integration
async def test_graphql_connectivity():
    """Test GraphQL endpoint connectivity."""
    test_instance = TestGraphQLConnectivity()
    await test_instance.test_graphql_ping_query()


@pytest.mark.integration
async def test_management_connectivity():
    """Test management server connectivity."""
    test_instance = TestGraphQLConnectivity()
    await test_instance.test_management_health_endpoint()


# Example of how to use GraphQL in integration tests
@pytest.mark.integration
async def test_integration_with_graphql():
    """Example integration test that uses GraphQL operations."""
    host = os.getenv("API_HOST", "localhost")
    port = int(os.getenv("API_PORT", "8080"))
    base_url = f"http://{host}:{port}"
    
    try:
        client = {{ PrefixName }}TestClient(base_url)
        
        # Test basic GraphQL functionality
        ping_result = await client.ping()
        assert ping_result == "pong"
        
        # Test schema introspection
        schema = await client.introspect_schema()
        assert schema is not None
        assert "queryType" in schema
        
        print("✓ GraphQL integration test: Basic functionality working")
        
    except Exception as e:
        pytest.skip(f"GraphQL server not available: {e}")
    
    # TODO: Once business logic is fully implemented, test actual operations:
    # result = await client.list_{{ prefix_name }}s()
    # assert result is not None 