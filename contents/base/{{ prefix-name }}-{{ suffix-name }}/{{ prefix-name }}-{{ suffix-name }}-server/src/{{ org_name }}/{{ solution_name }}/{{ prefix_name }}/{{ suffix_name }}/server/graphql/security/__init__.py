"""
GraphQL security for {{ PrefixName }}{{ SuffixName }}.

This package provides comprehensive GraphQL security including
query complexity limits, depth limits, rate limiting, authentication,
authorization, and input validation.
"""

from .extensions import (
    QueryComplexityExtension,
    QueryDepthExtension,
    RateLimitExtension,
    ErrorMaskingExtension,
    SecurityLoggingExtension,
    InputSanitizationExtension,
    create_security_extensions
)

from .permissions import (
    IsAuthenticated,
    IsAdmin,
    IsOwner,
    HasRole,
    IsAdminOrOwner,
    CommonPermissions
)

from .validators import (
    GraphQLSecurityValidator,
    QueryAnalyzer
)

from .config import get_security_config

__all__ = [
    # Extensions
    "QueryComplexityExtension",
    "QueryDepthExtension", 
    "RateLimitExtension",
    "ErrorMaskingExtension",
    "SecurityLoggingExtension",
    "InputSanitizationExtension",
    "create_security_extensions",
    
    # Permissions
    "IsAuthenticated",
    "IsAdmin",
    "IsOwner", 
    "HasRole",
    "IsAdminOrOwner",
    "CommonPermissions",
    
    # Validators
    "GraphQLSecurityValidator",
    "QueryAnalyzer",
    
    # Config
    "get_security_config"
] 