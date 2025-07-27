"""
Simple GraphQL test client for integration tests.

This module provides a lightweight GraphQL client specifically designed for testing
without requiring the full client package dependency.
"""

import json
from typing import Dict, Any, Optional, Union
import httpx


class GraphQLError(Exception):
    """Exception raised when GraphQL operations return errors."""
    
    def __init__(self, errors: list):
        self.errors = errors
        error_messages = [error.get('message', str(error)) for error in errors]
        super().__init__(f"GraphQL errors: {', '.join(error_messages)}")


class GraphQLTestClient:
    """
    Simple GraphQL client for integration testing.
    
    Provides basic GraphQL query/mutation execution with error handling
    and response validation.
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the GraphQL test client.
        
        Args:
            base_url: Base URL of the GraphQL service
            headers: Optional additional headers to include in requests
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.headers.setdefault('Content-Type', 'application/json')
    
    async def execute(
        self, 
        query: str, 
        variables: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query or mutation.
        
        Args:
            query: GraphQL query or mutation string
            variables: Optional variables for the query
            timeout: Request timeout in seconds
            
        Returns:
            GraphQL response data
            
        Raises:
            GraphQLError: If the GraphQL response contains errors
            httpx.HTTPError: If the HTTP request fails
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/graphql",
                json=payload,
                headers=self.headers
            )
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse GraphQL response
            result = response.json()
            
            # Check for GraphQL errors
            if 'errors' in result:
                raise GraphQLError(result['errors'])
            
            # Return the data portion
            return result.get('data', {})
    
    async def health_check(self) -> bool:
        """
        Perform a simple health check using GraphQL ping.
        
        Returns:
            True if the service is healthy, False otherwise
        """
        try:
            result = await self.execute('query { ping }')
            return result.get('ping') == 'pong'
        except Exception:
            return False
    
    async def introspect_schema(self) -> Dict[str, Any]:
        """
        Perform GraphQL introspection to get schema information.
        
        Returns:
            Schema introspection result
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    name
                    kind
                    description
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        result = await self.execute(introspection_query)
        return result.get('__schema', {})


class {{ PrefixName }}TestOperations:
    """
    GraphQL operations specifically for testing {{ PrefixName }}{{ SuffixName }} service.
    
    Contains pre-built queries and mutations for common test scenarios.
    """
    
    @staticmethod
    def ping_query() -> str:
        """Simple ping query for connectivity testing."""
        return "query { ping }"
    
    @staticmethod
    def get_{{ prefix_name }}_query() -> str:
        """Query to get a single {{ prefix_name }} by ID."""
        return """
        query Get{{ PrefixName }}($id: ID!) {
            get{{ PrefixName }}(id: $id) {
                id
                name
                description
                createdAt
                updatedAt
            }
        }
        """
    
    @staticmethod
    def list_{{ prefix_name }}s_query() -> str:
        """Query to list {{ prefix_name }}s with pagination."""
        return """
        query List{{ PrefixName }}s($pagination: PaginationInput, $filter: {{ PrefixName }}Filter) {
            list{{ PrefixName }}s(pagination: $pagination, filter: $filter) {
                edges {
                    node {
                        id
                        name
                        description
                        createdAt
                        updatedAt
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
                totalCount
            }
        }
        """
    
    @staticmethod
    def create_{{ prefix_name }}_mutation() -> str:
        """Mutation to create a new {{ prefix_name }}."""
        return """
        mutation Create{{ PrefixName }}($input: Create{{ PrefixName }}Input!) {
            create{{ PrefixName }}(input: $input) {
                success
                message
                {{ prefix_name }} {
                    id
                    name
                    description
                    createdAt
                    updatedAt
                }
                errors
            }
        }
        """
    
    @staticmethod
    def update_{{ prefix_name }}_mutation() -> str:
        """Mutation to update an existing {{ prefix_name }}."""
        return """
        mutation Update{{ PrefixName }}($id: ID!, $input: Update{{ PrefixName }}Input!) {
            update{{ PrefixName }}(id: $id, input: $input) {
                success
                message
                {{ prefix_name }} {
                    id
                    name
                    description
                    createdAt
                    updatedAt
                }
                errors
            }
        }
        """
    
    @staticmethod
    def delete_{{ prefix_name }}_mutation() -> str:
        """Mutation to delete a {{ prefix_name }}."""
        return """
        mutation Delete{{ PrefixName }}($input: Delete{{ PrefixName }}Input!) {
            delete{{ PrefixName }}(input: $input) {
                success
                message
                errors
            }
        }
        """


class {{ PrefixName }}GraphQLClient:
    """
    High-level GraphQL client for {{ PrefixName }}{{ SuffixName }} GraphQL operations.
    
    Provides convenient methods for common test operations with proper typing
    and error handling.
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize the {{ PrefixName }} test client."""
        self.client = GraphQLTestClient(base_url, headers)
        self.operations = {{ PrefixName }}TestOperations()
    
    async def ping(self) -> str:
        """Test connectivity with ping query."""
        result = await self.client.execute(self.operations.ping_query())
        return result.get('ping', '')
    
    async def get_{{ prefix_name }}(self, {{ prefix_name }}_id: str) -> Optional[Dict[str, Any]]:
        """Get a {{ prefix_name }} by ID."""
        try:
            result = await self.client.execute(
                self.operations.get_{{ prefix_name }}_query(),
                {'id': {{ prefix_name }}_id}
            )
            return result.get('get{{ PrefixName }}')
        except GraphQLError:
            return None
    
    async def list_{{ prefix_name }}s(
        self, 
        pagination: Optional[Dict[str, Any]] = None,
        filter_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List {{ prefix_name }}s with optional pagination and filtering."""
        variables = {}
        if pagination:
            variables['pagination'] = pagination
        if filter_args:
            variables['filter'] = filter_args
            
        result = await self.client.execute(
            self.operations.list_{{ prefix_name }}s_query(),
            variables
        )
        return result.get('list{{ PrefixName }}s', {})
    
    async def create_{{ prefix_name }}(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new {{ prefix_name }}."""
        result = await self.client.execute(
            self.operations.create_{{ prefix_name }}_mutation(),
            {'input': input_data}
        )
        return result.get('create{{ PrefixName }}', {})
    
    async def update_{{ prefix_name }}(
        self, 
        {{ prefix_name }}_id: str, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing {{ prefix_name }}."""
        result = await self.client.execute(
            self.operations.update_{{ prefix_name }}_mutation(),
            {'id': {{ prefix_name }}_id, 'input': input_data}
        )
        return result.get('update{{ PrefixName }}', {})
    
    async def delete_{{ prefix_name }}(self, {{ prefix_name }}_id: str) -> Dict[str, Any]:
        """Delete a {{ prefix_name }}."""
        result = await self.client.execute(
            self.operations.delete_{{ prefix_name }}_mutation(),
            {'input': {'id': {{ prefix_name }}_id}}
        )
        return result.get('delete{{ PrefixName }}', {})
    
    async def introspect_schema(self) -> Dict[str, Any]:
        """Get schema introspection data."""
        return await self.client.introspect_schema()
    
    async def health_check(self) -> bool:
        """Check if the GraphQL service is healthy."""
        return await self.client.health_check() 