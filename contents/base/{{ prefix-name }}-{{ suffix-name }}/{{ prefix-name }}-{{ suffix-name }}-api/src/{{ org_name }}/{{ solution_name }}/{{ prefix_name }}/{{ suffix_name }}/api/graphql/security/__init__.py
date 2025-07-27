"""
GraphQL security package for {{ PrefixName }}{{ SuffixName }}.

This package provides comprehensive security features for GraphQL operations,
including query complexity analysis, depth limiting, field-level authorization,
rate limiting, error masking, and input sanitization.
"""

from .extensions import (
    QueryComplexityExtension,
    QueryDepthExtension,
    RateLimitExtension,
    ErrorMaskingExtension,
    SecurityLoggingExtension,
    InputSanitizationExtension
)

from .permissions import (
    IsAuthenticated,
    IsAdmin,
    IsOwner,
    HasRole,
    IsAdminOrOwner,
    SecurityPermissionChecker
)

from .validators import (
    GraphQLSecurityValidator,
    QueryAnalyzer,
    SecurityRuleEngine
)

from .middleware import (
    CSRFProtectionMiddleware,
    SecurityHeadersMiddleware,
    GraphQLSecurityMiddleware
)

from .config import (
    SecurityConfig,
    get_security_config
)

__all__ = [
    # Extensions
    "QueryComplexityExtension",
    "QueryDepthExtension", 
    "RateLimitExtension",
    "ErrorMaskingExtension",
    "SecurityLoggingExtension",
    "InputSanitizationExtension",
    
    # Permissions
    "IsAuthenticated",
    "IsAdmin",
    "IsOwner",
    "HasRole",
    "IsAdminOrOwner",
    "SecurityPermissionChecker",
    
    # Validators
    "GraphQLSecurityValidator",
    "QueryAnalyzer",
    "SecurityRuleEngine",
    
    # Middleware
    "CSRFProtectionMiddleware",
    "SecurityHeadersMiddleware",
    "GraphQLSecurityMiddleware",
    
    # Config
    "SecurityConfig",
    "get_security_config"
] 