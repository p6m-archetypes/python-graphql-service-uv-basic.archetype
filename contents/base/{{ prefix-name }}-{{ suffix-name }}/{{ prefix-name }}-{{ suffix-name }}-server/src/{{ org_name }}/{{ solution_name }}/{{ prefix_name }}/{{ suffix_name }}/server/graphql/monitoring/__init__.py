"""
GraphQL monitoring for {{ PrefixName }}{{ SuffixName }}.

This package provides Prometheus metrics collection and observability
for GraphQL operations including request rates, duration, complexity,
and error tracking.
"""

from .extensions import (
    MetricsExtension,
    LoggingExtension,
    create_monitoring_extensions,
    get_prometheus_metrics
)

__all__ = [
    "MetricsExtension",
    "LoggingExtension", 
    "create_monitoring_extensions",
    "get_prometheus_metrics"
] 