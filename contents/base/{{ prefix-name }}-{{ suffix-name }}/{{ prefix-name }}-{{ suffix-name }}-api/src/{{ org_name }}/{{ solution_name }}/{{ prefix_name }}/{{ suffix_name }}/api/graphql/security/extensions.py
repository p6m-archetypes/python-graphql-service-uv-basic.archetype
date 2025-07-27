"""
GraphQL security extensions for {{ PrefixName }}{{ SuffixName }}.

This module provides comprehensive security extensions that protect against
common GraphQL vulnerabilities including query complexity attacks, depth bombing,
rate limiting violations, and information leakage through error messages.
"""

import time
import logging
import re
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import strawberry
from strawberry.extensions import Extension
from strawberry.types import ExecutionResult
from graphql import GraphQLError, DocumentNode, visit, Visitor
from graphql.language import ast

logger = logging.getLogger(__name__)


@dataclass
class SecurityMetrics:
    """Security metrics tracking for monitoring and alerting."""
    
    blocked_complex_queries: int = 0
    blocked_deep_queries: int = 0
    rate_limited_requests: int = 0
    masked_errors: int = 0
    sanitized_inputs: int = 0
    total_requests: int = 0
    security_violations: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_violation(self, violation_type: str, details: Dict[str, Any]):
        """Add a security violation to the tracking."""
        self.security_violations.append({
            "type": violation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        })
        
        # Keep only last 1000 violations to prevent memory bloat
        if len(self.security_violations) > 1000:
            self.security_violations = self.security_violations[-1000:]


# Global security metrics instance
security_metrics = SecurityMetrics()


class QueryComplexityExtension(Extension):
    """
    Extension to prevent DoS attacks through overly complex GraphQL queries.
    
    Analyzes query complexity by counting field selections, nested objects,
    and applying complexity multipliers for list fields and connections.
    """
    
    def __init__(
        self,
        maximum_complexity: int = 100,
        introspection_complexity: int = 10,
        list_multiplier: int = 5,
        connection_multiplier: int = 10,
        enable_logging: bool = True
    ):
        """
        Initialize query complexity extension.
        
        Args:
            maximum_complexity: Maximum allowed query complexity score
            introspection_complexity: Complexity score for introspection queries
            list_multiplier: Multiplier for list fields
            connection_multiplier: Multiplier for connection fields
            enable_logging: Whether to log complexity violations
        """
        self.maximum_complexity = maximum_complexity
        self.introspection_complexity = introspection_complexity
        self.list_multiplier = list_multiplier
        self.connection_multiplier = connection_multiplier
        self.enable_logging = enable_logging
    
    def on_request(self):
        """Analyze query complexity before execution."""
        if hasattr(self.execution_context, 'query') and self.execution_context.query:
            complexity = self._calculate_complexity(self.execution_context.query)
            
            # Check if query exceeds complexity limit
            if complexity > self.maximum_complexity:
                security_metrics.blocked_complex_queries += 1
                security_metrics.add_violation("query_complexity", {
                    "complexity": complexity,
                    "limit": self.maximum_complexity,
                    "query": str(self.execution_context.query)[:500]  # Truncated for logging
                })
                
                if self.enable_logging:
                    logger.warning(
                        f"Query complexity violation: {complexity} > {self.maximum_complexity}",
                        extra={
                            "complexity": complexity,
                            "limit": self.maximum_complexity,
                            "client_ip": self._get_client_ip()
                        }
                    )
                
                raise GraphQLError(
                    f"Query complexity {complexity} exceeds maximum allowed complexity {self.maximum_complexity}"
                )
        
        security_metrics.total_requests += 1
        yield
    
    def _calculate_complexity(self, document: DocumentNode) -> int:
        """Calculate the complexity score of a GraphQL query."""
        complexity_visitor = ComplexityAnalysisVisitor(
            list_multiplier=self.list_multiplier,
            connection_multiplier=self.connection_multiplier,
            introspection_complexity=self.introspection_complexity
        )
        visit(document, complexity_visitor)
        return complexity_visitor.complexity
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request context."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "client"):
                return request.client.host
        except:
            pass
        return "unknown"


class ComplexityAnalysisVisitor(Visitor):
    """Visitor to analyze GraphQL query complexity."""
    
    def __init__(self, list_multiplier: int = 5, connection_multiplier: int = 10, introspection_complexity: int = 10):
        self.complexity = 0
        self.list_multiplier = list_multiplier
        self.connection_multiplier = connection_multiplier
        self.introspection_complexity = introspection_complexity
        self.depth = 0
        self.in_introspection = False
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Calculate complexity when entering a field."""
        field_name = node.name.value
        
        # Check if this is an introspection query
        if field_name.startswith("__"):
            self.in_introspection = True
            self.complexity += self.introspection_complexity
            return
        
        # Base complexity for each field
        field_complexity = 1
        
        # Apply multipliers based on field type patterns
        if any(pattern in field_name.lower() for pattern in ["list", "all", "many"]):
            field_complexity *= self.list_multiplier
        
        if any(pattern in field_name.lower() for pattern in ["connection", "edge"]):
            field_complexity *= self.connection_multiplier
        
        # Increase complexity based on nesting depth
        field_complexity += self.depth
        
        self.complexity += field_complexity
        self.depth += 1
    
    def leave_field(self, node: ast.FieldNode, *_):
        """Decrease depth when leaving a field."""
        self.depth -= 1
        if node.name.value.startswith("__"):
            self.in_introspection = False


class QueryDepthExtension(Extension):
    """
    Extension to prevent DoS attacks through deeply nested GraphQL queries.
    
    Analyzes query depth and blocks queries that exceed the maximum allowed depth.
    """
    
    def __init__(self, max_depth: int = 15, enable_logging: bool = True):
        """
        Initialize query depth extension.
        
        Args:
            max_depth: Maximum allowed query nesting depth
            enable_logging: Whether to log depth violations
        """
        self.max_depth = max_depth
        self.enable_logging = enable_logging
    
    def on_request(self):
        """Analyze query depth before execution."""
        if hasattr(self.execution_context, 'query') and self.execution_context.query:
            depth = self._calculate_depth(self.execution_context.query)
            
            if depth > self.max_depth:
                security_metrics.blocked_deep_queries += 1
                security_metrics.add_violation("query_depth", {
                    "depth": depth,
                    "limit": self.max_depth,
                    "query": str(self.execution_context.query)[:500]
                })
                
                if self.enable_logging:
                    logger.warning(
                        f"Query depth violation: {depth} > {self.max_depth}",
                        extra={
                            "depth": depth,
                            "limit": self.max_depth,
                            "client_ip": self._get_client_ip()
                        }
                    )
                
                raise GraphQLError(
                    f"Query depth {depth} exceeds maximum allowed depth {self.max_depth}"
                )
        
        yield
    
    def _calculate_depth(self, document: DocumentNode) -> int:
        """Calculate the maximum depth of a GraphQL query."""
        depth_visitor = DepthAnalysisVisitor()
        visit(document, depth_visitor)
        return depth_visitor.max_depth
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request context."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "client"):
                return request.client.host
        except:
            pass
        return "unknown"


class DepthAnalysisVisitor(Visitor):
    """Visitor to analyze GraphQL query depth."""
    
    def __init__(self):
        self.depth = 0
        self.max_depth = 0
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Increase depth when entering a field."""
        self.depth += 1
        self.max_depth = max(self.max_depth, self.depth)
    
    def leave_field(self, node: ast.FieldNode, *_):
        """Decrease depth when leaving a field."""
        self.depth -= 1


class RateLimitExtension(Extension):
    """
    Extension to implement rate limiting for GraphQL operations.
    
    Tracks requests per client IP and enforces rate limits with sliding window.
    """
    
    def __init__(
        self,
        rate_limit: int = 100,
        time_window: int = 60,
        burst_limit: int = 20,
        enable_logging: bool = True
    ):
        """
        Initialize rate limiting extension.
        
        Args:
            rate_limit: Maximum requests per time window
            time_window: Time window in seconds for rate limiting
            burst_limit: Maximum burst requests allowed
            enable_logging: Whether to log rate limit violations
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.burst_limit = burst_limit
        self.enable_logging = enable_logging
        
        # Request tracking with sliding window
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque())
        self.burst_counts: Dict[str, int] = defaultdict(int)
        self.last_reset: Dict[str, float] = defaultdict(float)
    
    def on_request(self):
        """Check rate limits before executing request."""
        client_ip = self._get_client_ip()
        current_time = time.time()
        
        # Clean up old requests (sliding window)
        self._cleanup_old_requests(client_ip, current_time)
        
        # Check burst limit (short-term protection)
        if self._check_burst_limit(client_ip, current_time):
            self._record_rate_limit_violation(client_ip, "burst")
            raise GraphQLError("Rate limit exceeded: too many requests in burst")
        
        # Check rate limit (long-term protection)
        if len(self.request_times[client_ip]) >= self.rate_limit:
            self._record_rate_limit_violation(client_ip, "rate")
            raise GraphQLError(f"Rate limit exceeded: {self.rate_limit} requests per {self.time_window} seconds")
        
        # Record this request
        self.request_times[client_ip].append(current_time)
        yield
    
    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Remove requests outside the time window."""
        cutoff_time = current_time - self.time_window
        
        while (self.request_times[client_ip] and 
               self.request_times[client_ip][0] < cutoff_time):
            self.request_times[client_ip].popleft()
    
    def _check_burst_limit(self, client_ip: str, current_time: float) -> bool:
        """Check if burst limit is exceeded."""
        # Reset burst counter every 10 seconds
        if current_time - self.last_reset[client_ip] > 10:
            self.burst_counts[client_ip] = 0
            self.last_reset[client_ip] = current_time
        
        self.burst_counts[client_ip] += 1
        return self.burst_counts[client_ip] > self.burst_limit
    
    def _record_rate_limit_violation(self, client_ip: str, violation_type: str):
        """Record rate limit violation for monitoring."""
        security_metrics.rate_limited_requests += 1
        security_metrics.add_violation("rate_limit", {
            "client_ip": client_ip,
            "violation_type": violation_type,
            "requests_in_window": len(self.request_times[client_ip]),
            "rate_limit": self.rate_limit,
            "time_window": self.time_window
        })
        
        if self.enable_logging:
            logger.warning(
                f"Rate limit violation from {client_ip}: {violation_type}",
                extra={
                    "client_ip": client_ip,
                    "violation_type": violation_type,
                    "requests_in_window": len(self.request_times[client_ip])
                }
            )
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request context."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "client"):
                return request.client.host
        except:
            pass
        return "unknown"


class ErrorMaskingExtension(Extension):
    """
    Extension to mask sensitive error information in production environments.
    
    Prevents information leakage through detailed error messages while maintaining
    proper logging for debugging purposes.
    """
    
    def __init__(
        self,
        mask_errors_in_production: bool = True,
        allowed_error_types: Set[str] = None,
        enable_logging: bool = True
    ):
        """
        Initialize error masking extension.
        
        Args:
            mask_errors_in_production: Whether to mask errors in production
            allowed_error_types: Set of error types that are safe to expose
            enable_logging: Whether to log masked errors
        """
        self.mask_errors_in_production = mask_errors_in_production
        self.allowed_error_types = allowed_error_types or {
            "ValidationError",
            "AuthenticationError", 
            "AuthorizationError"
        }
        self.enable_logging = enable_logging
    
    def on_execute(self):
        """Mask errors after execution if needed."""
        yield
        
        if (self.mask_errors_in_production and 
            self.execution_context.result and 
            self.execution_context.result.errors):
            
            for i, error in enumerate(self.execution_context.result.errors):
                if self._should_mask_error(error):
                    original_message = str(error)
                    
                    # Log the original error for debugging
                    if self.enable_logging:
                        logger.error(
                            f"Masked GraphQL error: {original_message}",
                            extra={
                                "original_error": original_message,
                                "error_type": type(error).__name__,
                                "client_ip": self._get_client_ip()
                            }
                        )
                    
                    # Replace with generic message
                    self.execution_context.result.errors[i] = GraphQLError(
                        "An internal error occurred. Please contact support if the problem persists."
                    )
                    
                    security_metrics.masked_errors += 1
                    security_metrics.add_violation("error_masked", {
                        "original_message": original_message[:200],  # Truncated
                        "error_type": type(error).__name__
                    })
    
    def _should_mask_error(self, error: GraphQLError) -> bool:
        """Determine if an error should be masked."""
        error_type = type(error).__name__
        
        # Don't mask allowed error types
        if error_type in self.allowed_error_types:
            return False
        
        # Don't mask errors with specific GraphQL error codes
        if hasattr(error, 'extensions') and error.extensions:
            error_code = error.extensions.get('code')
            if error_code in ['GRAPHQL_VALIDATION_FAILED', 'GRAPHQL_PARSE_FAILED']:
                return False
        
        # Mask all other errors
        return True
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request context."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "client"):
                return request.client.host
        except:
            pass
        return "unknown"


class SecurityLoggingExtension(Extension):
    """
    Extension for comprehensive security event logging and monitoring.
    
    Logs all GraphQL operations with security-relevant information for
    audit trails and threat detection.
    """
    
    def __init__(
        self,
        log_all_operations: bool = True,
        log_introspection: bool = True,
        log_failed_operations: bool = True,
        sensitive_fields: Set[str] = None
    ):
        """
        Initialize security logging extension.
        
        Args:
            log_all_operations: Whether to log all GraphQL operations
            log_introspection: Whether to log introspection queries
            log_failed_operations: Whether to log failed operations
            sensitive_fields: Set of field names to redact from logs
        """
        self.log_all_operations = log_all_operations
        self.log_introspection = log_introspection
        self.log_failed_operations = log_failed_operations
        self.sensitive_fields = sensitive_fields or {
            "password", "token", "secret", "key", "credential"
        }
    
    def on_request(self):
        """Log security information about the request."""
        start_time = time.time()
        client_ip = self._get_client_ip()
        user_agent = self._get_user_agent()
        operation_name = self._get_operation_name()
        
        if self.log_all_operations:
            logger.info(
                f"GraphQL request started: {operation_name}",
                extra={
                    "event_type": "graphql_request_start",
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "operation_name": operation_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        yield
        
        # Log completion information
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # milliseconds
        
        has_errors = (self.execution_context.result and 
                     self.execution_context.result.errors)
        
        if has_errors and self.log_failed_operations:
            logger.warning(
                f"GraphQL request failed: {operation_name}",
                extra={
                    "event_type": "graphql_request_failed",
                    "client_ip": client_ip,
                    "operation_name": operation_name,
                    "execution_time_ms": execution_time,
                    "error_count": len(self.execution_context.result.errors),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        elif self.log_all_operations:
            logger.info(
                f"GraphQL request completed: {operation_name}",
                extra={
                    "event_type": "graphql_request_completed",
                    "client_ip": client_ip,
                    "operation_name": operation_name,
                    "execution_time_ms": execution_time,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request context."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "client"):
                return request.client.host
        except:
            pass
        return "unknown"
    
    def _get_user_agent(self) -> str:
        """Get user agent from request headers."""
        try:
            request = self.execution_context.context.get("request")
            if request and hasattr(request, "headers"):
                return request.headers.get("user-agent", "unknown")
        except:
            pass
        return "unknown"
    
    def _get_operation_name(self) -> str:
        """Get operation name from GraphQL query."""
        try:
            if hasattr(self.execution_context, 'query') and self.execution_context.query:
                for definition in self.execution_context.query.definitions:
                    if hasattr(definition, 'name') and definition.name:
                        return definition.name.value
                    elif hasattr(definition, 'operation'):
                        return f"{definition.operation}_operation"
        except:
            pass
        return "unknown_operation"


class InputSanitizationExtension(Extension):
    """
    Extension for sanitizing GraphQL input values to prevent injection attacks.
    
    Validates and sanitizes input parameters to prevent various injection
    attacks and malicious input processing.
    """
    
    def __init__(
        self,
        enable_html_sanitization: bool = True,
        enable_sql_injection_detection: bool = True,
        enable_script_detection: bool = True,
        max_string_length: int = 10000
    ):
        """
        Initialize input sanitization extension.
        
        Args:
            enable_html_sanitization: Whether to sanitize HTML in inputs
            enable_sql_injection_detection: Whether to detect SQL injection attempts
            enable_script_detection: Whether to detect script injection attempts
            max_string_length: Maximum allowed string input length
        """
        self.enable_html_sanitization = enable_html_sanitization
        self.enable_sql_injection_detection = enable_sql_injection_detection
        self.enable_script_detection = enable_script_detection
        self.max_string_length = max_string_length
        
        # Patterns for detecting malicious inputs
        self.sql_injection_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\b(exec|execute)\b.*\()",
            r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
            r"('.*'.*=.*'.*')",
            r"(\b1\s*=\s*1\b)",
            r"(\b0\s*=\s*1\b)"
        ]
        
        self.script_injection_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\("
        ]
    
    def on_execute(self):
        """Sanitize inputs before execution."""
        if hasattr(self.execution_context, 'variable_values'):
            self._sanitize_variables(self.execution_context.variable_values)
        
        yield
    
    def _sanitize_variables(self, variables: Dict[str, Any]):
        """Recursively sanitize all variables."""
        for key, value in variables.items():
            if isinstance(value, str):
                sanitized_value = self._sanitize_string(value, key)
                if sanitized_value != value:
                    variables[key] = sanitized_value
                    security_metrics.sanitized_inputs += 1
                    logger.info(f"Sanitized input variable: {key}")
            elif isinstance(value, dict):
                self._sanitize_variables(value)
            elif isinstance(value, list):
                self._sanitize_list(value)
    
    def _sanitize_list(self, items: List[Any]):
        """Sanitize items in a list."""
        for i, item in enumerate(items):
            if isinstance(item, str):
                sanitized_item = self._sanitize_string(item, f"list_item_{i}")
                if sanitized_item != item:
                    items[i] = sanitized_item
                    security_metrics.sanitized_inputs += 1
            elif isinstance(item, dict):
                self._sanitize_variables(item)
            elif isinstance(item, list):
                self._sanitize_list(item)
    
    def _sanitize_string(self, value: str, field_name: str) -> str:
        """Sanitize a string value."""
        original_value = value
        
        # Check string length
        if len(value) > self.max_string_length:
            logger.warning(f"Input too long for field {field_name}: {len(value)} > {self.max_string_length}")
            value = value[:self.max_string_length]
        
        # Detect and prevent SQL injection
        if self.enable_sql_injection_detection:
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(f"Potential SQL injection detected in field {field_name}")
                    security_metrics.add_violation("sql_injection_attempt", {
                        "field_name": field_name,
                        "pattern": pattern,
                        "value": value[:100]  # Truncated for security
                    })
                    # Replace suspicious patterns
                    value = re.sub(pattern, "[SANITIZED]", value, flags=re.IGNORECASE)
        
        # Detect and prevent script injection
        if self.enable_script_detection:
            for pattern in self.script_injection_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(f"Potential script injection detected in field {field_name}")
                    security_metrics.add_violation("script_injection_attempt", {
                        "field_name": field_name,
                        "pattern": pattern,
                        "value": value[:100]  # Truncated for security
                    })
                    # Replace suspicious patterns
                    value = re.sub(pattern, "[SANITIZED]", value, flags=re.IGNORECASE)
        
        # HTML sanitization
        if self.enable_html_sanitization:
            # Basic HTML tag removal
            value = re.sub(r'<[^>]+>', '', value)
            
            # HTML entity decoding to prevent bypass
            html_entities = {
                '&lt;': '<', '&gt;': '>', '&amp;': '&',
                '&quot;': '"', '&#x27;': "'", '&#x2F;': '/',
                '&#96;': '`', '&#x60;': '`'
            }
            for entity, char in html_entities.items():
                value = value.replace(entity, char)
        
        return value


def get_security_metrics() -> SecurityMetrics:
    """Get current security metrics for monitoring."""
    return security_metrics


def reset_security_metrics():
    """Reset security metrics (useful for testing)."""
    global security_metrics
    security_metrics = SecurityMetrics() 