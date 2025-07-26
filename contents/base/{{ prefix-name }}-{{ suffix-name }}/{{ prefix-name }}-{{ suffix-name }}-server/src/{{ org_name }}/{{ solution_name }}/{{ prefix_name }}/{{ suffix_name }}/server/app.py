"""
FastAPI application factory for the {{ PrefixName }}{{ SuffixName }} service.

This module creates and configures the main FastAPI application for the REST API.
Similar to how the gRPC archetype has gRPC service implementations that delegate to core services,
this FastAPI app provides REST endpoints and GraphQL resolvers that delegate to the same business logic.
It now includes full real-time subscription support via WebSocket connections.
"""

import logging
from typing import Dict, Any, Optional

import structlog
from fastapi import FastAPI, HTTPException, Depends, Query, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import ValidationError
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

from .config.settings import get_settings
from .middleware.auth import get_auth_service

# Import GraphQL schema
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql import schema

# Import subscription event bus
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.subscriptions.event_bus import (
    initialize_event_bus,
    shutdown_event_bus
)

# Note: These imports will work once we set up proper dependencies
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core.example_service_core import ExampleServiceCore
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories.example_repository import ExampleRepository

logger = structlog.get_logger()


def create_app(settings: Optional[Any] = None) -> FastAPI:
    """
    Application factory function.
    
    Args:
        settings: Optional settings override
    
    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Add CORS middleware
    _add_cors_middleware(app, settings)

    # Add exception handlers
    _add_exception_handlers(app)

    # Add GraphQL endpoint with WebSocket support
    _add_graphql_router(app, settings)

    # Add routes (thin wrappers that delegate to business services)
    _add_routes(app)

    # Add event handlers for startup/shutdown
    _add_event_handlers(app)

    logger.info(
        "FastAPI application created",
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
        graphql_enabled=True,
        websockets_enabled=True
    )

    return app


def _add_cors_middleware(app: FastAPI, settings: Any) -> None:
    """Add CORS middleware configuration."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )


def _add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers."""

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation failed", "details": exc.errors()}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )


def _add_graphql_router(app: FastAPI, settings) -> None:
    """Add GraphQL endpoint with WebSocket support to the FastAPI application."""

    # Enable GraphiQL/Playground in development or when explicitly enabled
    graphiql_enabled = (settings.debug or settings.graphql_playground_enabled) and settings.is_development

    # Create GraphQL router with WebSocket subscription support
    graphql_router = GraphQLRouter(
        schema,
        graphiql=graphiql_enabled,
        path=settings.graphql_endpoint,
        subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL],
        # Enable introspection based on settings
        introspection=settings.graphql_introspection_enabled,
    )

    # Include the GraphQL router (no prefix since path is already specified)
    app.include_router(graphql_router, tags=["GraphQL"])

    # Add WebSocket route for GraphQL subscriptions
    app.add_websocket_route(settings.graphql_endpoint, graphql_router)

    logger.info(
        "GraphQL endpoint configured with WebSocket support",
        path=settings.graphql_endpoint,
        graphiql_enabled=graphiql_enabled,
        introspection_enabled=settings.graphql_introspection_enabled,
        websocket_enabled=True,
        subscription_protocols=["graphql-transport-ws"],
        max_query_depth=settings.graphql_max_query_depth,
        max_query_complexity=settings.graphql_max_query_complexity
    )


def _add_routes(app: FastAPI) -> None:
    """Add API routes that delegate to business services."""

    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Returns:
            Dict containing health status
        """
        return {
            "status": "healthy",
            "service": "{{ prefix-name }}-{{ suffix-name }}",
            "version": "0.1.0",
            "graphql_enabled": True,
            "websockets_enabled": True
        }

    @app.get("/metrics")
    async def metrics(response: Response) -> Response:
        """
        Prometheus metrics endpoint.
        
        Returns:
            Prometheus formatted metrics
        """
        data = generate_latest()
        response = Response(content=data, media_type=CONTENT_TYPE_LATEST)
        return response

    # TODO: Add more REST endpoints as needed
    # These would delegate to the same business services that GraphQL uses
    
    @app.get("/api/{{ prefix_name }}s")
    async def list_{{ prefix_name }}s(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ) -> Dict[str, Any]:
        """
        REST endpoint to list {{ prefix_name }}s.
        This demonstrates how REST and GraphQL can coexist.
        """
        # TODO: Implement using the same business services as GraphQL
        return {
            "{{ prefix_name }}s": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "message": "REST endpoint - use GraphQL for full functionality including real-time subscriptions"
        }


def _add_event_handlers(app: FastAPI) -> None:
    """Add startup and shutdown event handlers."""

    @app.on_event("startup")
    async def startup_event():
        """
        Startup event handler.
        
        Initializes the event bus for GraphQL subscriptions and other
        application-level resources.
        """
        logger.info("Starting {{ PrefixName }}{{ SuffixName }} server...")
        
        try:
            # Initialize the event bus for subscriptions
            await initialize_event_bus()
            logger.info("GraphQL subscription event bus initialized")
            
            # TODO: Initialize other resources like database connections
            # db_manager = get_database_manager()
            # await db_manager.initialize()
            
            # TODO: Initialize repositories and services
            # await initialize_repositories()
            
            logger.info("{{ PrefixName }}{{ SuffixName }} server startup complete")
            
        except Exception as e:
            logger.error("Failed to start server", error=str(e))
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Shutdown event handler.
        
        Cleans up resources including the event bus and database connections.
        """
        logger.info("Shutting down {{ PrefixName }}{{ SuffixName }} server...")
        
        try:
            # Shutdown the event bus
            await shutdown_event_bus()
            logger.info("GraphQL subscription event bus shutdown complete")
            
            # TODO: Cleanup other resources
            # await cleanup_database_connections()
            # await cleanup_repositories()
            
            logger.info("{{ PrefixName }}{{ SuffixName }} server shutdown complete")
            
        except Exception as e:
            logger.error("Error during server shutdown", error=str(e))


# Create the application instance
app = create_app() 