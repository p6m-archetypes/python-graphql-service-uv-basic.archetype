"""
Pytest configuration and fixtures for integration tests.

This module provides shared fixtures and configuration for all integration tests,
including GraphQL client setup and environment configuration.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator

from tests.utils.graphql_test_client import GraphQLTestClient, {{ PrefixName }}TestClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration from environment variables."""
    return {
        "api_host": os.getenv("API_HOST", "localhost"),
        "api_port": int(os.getenv("API_PORT", "8080")),
        "management_host": os.getenv("MANAGEMENT_HOST", "localhost"), 
        "management_port": int(os.getenv("MANAGEMENT_PORT", "8080")),
        "database_url": os.getenv("DATABASE_URL", "postgresql://localhost:5432/{{ prefix_name }}_{{ suffix_name }}_test"),
        "test_timeout": float(os.getenv("TEST_TIMEOUT", "30.0")),
    }


@pytest.fixture(scope="session")
async def base_url(test_config) -> str:
    """Provide the base URL for the GraphQL service."""
    return f"http://{test_config['api_host']}:{test_config['api_port']}"


@pytest.fixture
async def graphql_client(base_url) -> AsyncGenerator[GraphQLTestClient, None]:
    """
    Provide a basic GraphQL test client for integration tests.
    
    This fixture creates a new client instance for each test to ensure isolation.
    """
    client = GraphQLTestClient(base_url)
    yield client
    # No cleanup needed for HTTP client


@pytest.fixture
async def {{ prefix_name }}_test_client(base_url) -> AsyncGenerator[{{ PrefixName }}TestClient, None]:
    """
    Provide a {{ PrefixName }}{{ SuffixName }}-specific test client for integration tests.
    
    This fixture includes pre-built queries and mutations for common test operations.
    """
    client = {{ PrefixName }}TestClient(base_url)
    yield client
    # No cleanup needed for HTTP client


@pytest.fixture(scope="session")
async def health_check(base_url):
    """
    Verify that the GraphQL service is healthy before running tests.
    
    This fixture runs once per session and skips all tests if the service is unavailable.
    """
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Test basic HTTP connectivity
            response = await client.get(f"{base_url}/health", timeout=10.0)
            if response.status_code not in [200, 503]:
                pytest.skip(f"Service health check failed: {response.status_code}")
            
            # Test GraphQL endpoint
            gql_client = GraphQLTestClient(base_url)
            health_result = await gql_client.health_check()
            if not health_result:
                pytest.skip("GraphQL endpoint health check failed")
                
    except Exception as e:
        pytest.skip(f"Service is not available: {e}")


@pytest.fixture(autouse=True)
async def ensure_service_ready(health_check):
    """
    Automatically ensure service is ready before each test.
    
    This fixture runs before every test and depends on the health_check fixture.
    """
    # The health_check fixture has already verified service availability
    pass


@pytest.fixture
def sample_{{ prefix_name }}_data():
    """Provide sample {{ prefix_name }} data for testing."""
    return {
        "name": "Test {{ PrefixName }}",
        "description": "A test {{ prefix_name }} for integration testing",
    }


@pytest.fixture
def sample_pagination_params():
    """Provide sample pagination parameters for testing."""
    return {
        "first": 10,
        "after": None
    }


@pytest.fixture 
def sample_filter_params():
    """Provide sample filter parameters for testing."""
    return {
        "name": "Test"
    }


# Pytest markers for test categorization
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_docker: mark test as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "graphql: mark test as GraphQL-specific"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to tests in unit directory  
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            
        # Add graphql marker to tests that use GraphQL clients
        if hasattr(item, 'fixturenames'):
            if any('graphql' in name for name in item.fixturenames):
                item.add_marker(pytest.mark.graphql) 