"""
GraphQL monitoring extensions for Prometheus metrics collection.

This module provides Strawberry GraphQL extensions that automatically
collect metrics for GraphQL operations and expose them for Prometheus.
"""

import time
import logging
from typing import Any, Generator, Optional
from strawberry.extensions import Extension
from strawberry.types import ExecutionContext
from strawberry.schema.exceptions import InvalidFieldArgument
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


# Prometheus Metrics
graphql_requests_total = Counter(
    'graphql_requests_total',
    'Total number of GraphQL requests',
    ['operation_type', 'operation_name', 'status']
)

graphql_request_duration_seconds = Histogram(
    'graphql_request_duration_seconds', 
    'Duration of GraphQL requests in seconds',
    ['operation_type', 'operation_name'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

graphql_errors_total = Counter(
    'graphql_errors_total',
    'Total number of GraphQL errors',
    ['error_type', 'operation_type', 'operation_name']
)

graphql_query_complexity = Histogram(
    'graphql_query_complexity',
    'Query complexity score for GraphQL operations',
    ['operation_type', 'operation_name'],
    buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000)
)

graphql_active_subscriptions = Gauge(
    'graphql_active_subscriptions',
    'Number of active GraphQL subscriptions'
)

graphql_field_resolvers_duration_seconds = Histogram(
    'graphql_field_resolvers_duration_seconds',
    'Duration of GraphQL field resolvers in seconds', 
    ['field_name', 'parent_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)


logger = logging.getLogger(__name__)


class MetricsExtension(Extension):
    """
    Strawberry extension that collects Prometheus metrics for GraphQL operations.
    
    Automatically tracks:
    - Request counts by operation type/name  
    - Request duration histograms
    - Error counts by type
    - Query complexity metrics
    - Active subscription counts
    """
    
    def on_execute(self) -> Generator[None, None, None]:
        """Track metrics for GraphQL execution."""
        start_time = time.time()
        
        # Extract operation details
        operation_name = self._get_operation_name()
        operation_type = self._get_operation_type()
        
        # Increment request counter
        graphql_requests_total.labels(
            operation_type=operation_type,
            operation_name=operation_name,
            status='started'
        ).inc()
        
        # Track active subscriptions
        if operation_type == 'subscription':
            graphql_active_subscriptions.inc()
        
        try:
            yield
            
            # Success metrics
            duration = time.time() - start_time
            graphql_request_duration_seconds.labels(
                operation_type=operation_type,
                operation_name=operation_name
            ).observe(duration)
            
            graphql_requests_total.labels(
                operation_type=operation_type,
                operation_name=operation_name,
                status='success'
            ).inc()
            
        except Exception as e:
            # Error metrics
            error_type = type(e).__name__
            graphql_errors_total.labels(
                error_type=error_type,
                operation_type=operation_type,
                operation_name=operation_name
            ).inc()
            
            graphql_requests_total.labels(
                operation_type=operation_type,
                operation_name=operation_name,
                status='error'
            ).inc()
            
            raise
        finally:
            # Cleanup subscription count
            if operation_type == 'subscription':
                graphql_active_subscriptions.dec()
    
    def on_validate(self) -> Generator[None, None, None]:
        """Track validation metrics."""
        try:
            yield
        except Exception as e:
            operation_name = self._get_operation_name()
            operation_type = self._get_operation_type()
            
            graphql_errors_total.labels(
                error_type='ValidationError',
                operation_type=operation_type,
                operation_name=operation_name
            ).inc()
            raise
    
    def _get_operation_name(self) -> str:
        """Get operation name from execution context."""
        if hasattr(self.execution_context, 'operation_name') and self.execution_context.operation_name:
            return self.execution_context.operation_name
        return 'anonymous'
    
    def _get_operation_type(self) -> str:
        """Get operation type from execution context.""" 
        if hasattr(self.execution_context, 'operation_type') and self.execution_context.operation_type:
            return self.execution_context.operation_type.value.lower()
        return 'query'


class LoggingExtension(Extension):
    """
    Strawberry extension that provides structured logging for GraphQL operations.
    
    Logs operation start/completion with timing and error details.
    """
    
    def on_execute(self) -> Generator[None, None, None]:
        """Log GraphQL execution details."""
        start_time = time.time()
        operation_name = self._get_operation_name()
        operation_type = self._get_operation_type()
        
        logger.info(
            f"GraphQL {operation_type} '{operation_name}' started",
            extra={
                'operation_type': operation_type,
                'operation_name': operation_name,
                'event': 'graphql_operation_start'
            }
        )
        
        try:
            yield
            
            duration = time.time() - start_time
            logger.info(
                f"GraphQL {operation_type} '{operation_name}' completed successfully in {duration:.3f}s",
                extra={
                    'operation_type': operation_type, 
                    'operation_name': operation_name,
                    'duration_seconds': duration,
                    'event': 'graphql_operation_success'
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"GraphQL {operation_type} '{operation_name}' failed after {duration:.3f}s: {str(e)}",
                extra={
                    'operation_type': operation_type,
                    'operation_name': operation_name,
                    'duration_seconds': duration,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'event': 'graphql_operation_error'
                },
                exc_info=True
            )
            raise
    
    def _get_operation_name(self) -> str:
        """Get operation name from execution context."""
        if hasattr(self.execution_context, 'operation_name') and self.execution_context.operation_name:
            return self.execution_context.operation_name
        return 'anonymous'
    
    def _get_operation_type(self) -> str:
        """Get operation type from execution context."""
        if hasattr(self.execution_context, 'operation_type') and self.execution_context.operation_type:
            return self.execution_context.operation_type.value.lower()
        return 'query'


def create_monitoring_extensions() -> list[Extension]:
    """
    Create the list of monitoring extensions for GraphQL schema.
    
    Returns:
        List of configured monitoring extensions
    """
    return [
        MetricsExtension(),
        LoggingExtension()
    ]


def get_prometheus_metrics() -> tuple[bytes, str]:
    """
    Get Prometheus metrics for HTTP endpoint.
    
    Returns:
        Tuple of (metrics_data, content_type)
    """
    return generate_latest().encode('utf-8'), CONTENT_TYPE_LATEST 