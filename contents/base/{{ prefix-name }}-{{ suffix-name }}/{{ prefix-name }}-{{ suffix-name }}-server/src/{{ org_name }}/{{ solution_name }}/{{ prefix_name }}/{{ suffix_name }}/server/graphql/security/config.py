"""
Security configuration for {{ PrefixName }}{{ SuffixName }} GraphQL API.

This module provides centralized configuration management for all
GraphQL security features including complexity limits, rate limiting,
error masking, and permission settings.
"""

import os
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(Enum):
    """Security level presets for different environments."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels for security events."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class QueryComplexityConfig:
    """Configuration for query complexity analysis."""
    
    enabled: bool = True
    maximum_complexity: int = 100
    introspection_complexity: int = 10
    list_multiplier: int = 5
    connection_multiplier: int = 10
    enable_logging: bool = True
    log_violations: bool = True


@dataclass
class QueryDepthConfig:
    """Configuration for query depth analysis."""
    
    enabled: bool = True
    max_depth: int = 15
    enable_logging: bool = True
    log_violations: bool = True


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    enabled: bool = True
    rate_limit: int = 100  # requests per time window
    time_window: int = 60  # seconds
    burst_limit: int = 20  # max burst requests
    enable_logging: bool = True
    log_violations: bool = True
    whitelist_ips: Set[str] = field(default_factory=set)
    blacklist_ips: Set[str] = field(default_factory=set)


@dataclass
class ErrorMaskingConfig:
    """Configuration for error masking."""
    
    enabled: bool = True
    mask_errors_in_production: bool = True
    allowed_error_types: Set[str] = field(default_factory=lambda: {
        "ValidationError",
        "AuthenticationError", 
        "AuthorizationError",
        "GraphQLError"
    })
    enable_logging: bool = True
    log_masked_errors: bool = True


@dataclass
class SecurityLoggingConfig:
    """Configuration for security logging."""
    
    enabled: bool = True
    log_all_operations: bool = False  # Can be verbose in production
    log_introspection: bool = True
    log_failed_operations: bool = True
    log_permission_checks: bool = True
    log_permission_denials: bool = True
    log_level: LogLevel = LogLevel.INFO
    sensitive_fields: Set[str] = field(default_factory=lambda: {
        "password", "token", "secret", "key", "credential", "auth"
    })


@dataclass
class InputSanitizationConfig:
    """Configuration for input sanitization."""
    
    enabled: bool = True
    enable_html_sanitization: bool = True
    enable_sql_injection_detection: bool = True
    enable_script_detection: bool = True
    max_string_length: int = 10000
    enable_logging: bool = True
    log_violations: bool = True


@dataclass
class PermissionConfig:
    """Configuration for permission system."""
    
    enabled: bool = True
    default_require_authentication: bool = False
    enable_permission_logging: bool = True
    log_permission_denials: bool = True
    enable_role_caching: bool = True
    role_cache_ttl: int = 300  # seconds


@dataclass
class CSRFConfig:
    """Configuration for CSRF protection."""
    
    enabled: bool = True
    require_csrf_token: bool = True
    csrf_header_name: str = "X-CSRF-Token"
    csrf_cookie_name: str = "csrf_token"
    trusted_origins: Set[str] = field(default_factory=set)


@dataclass
class SecurityHeadersConfig:
    """Configuration for security headers."""
    
    enabled: bool = True
    content_security_policy: str = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    referrer_policy: str = "strict-origin-when-cross-origin"


@dataclass
class SecurityConfig:
    """
    Master security configuration for GraphQL API.
    
    This configuration class aggregates all security-related settings
    and provides methods for loading from environment variables or files.
    """
    
    # Security level
    security_level: SecurityLevel = SecurityLevel.PRODUCTION
    
    # Component configurations
    query_complexity: QueryComplexityConfig = field(default_factory=QueryComplexityConfig)
    query_depth: QueryDepthConfig = field(default_factory=QueryDepthConfig)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    error_masking: ErrorMaskingConfig = field(default_factory=ErrorMaskingConfig)
    security_logging: SecurityLoggingConfig = field(default_factory=SecurityLoggingConfig)
    input_sanitization: InputSanitizationConfig = field(default_factory=InputSanitizationConfig)
    permissions: PermissionConfig = field(default_factory=PermissionConfig)
    csrf_protection: CSRFConfig = field(default_factory=CSRFConfig)
    security_headers: SecurityHeadersConfig = field(default_factory=SecurityHeadersConfig)
    
    # Global settings
    enable_introspection: bool = False
    enable_playground: bool = False
    enable_debug_mode: bool = False
    
    @classmethod
    def for_environment(cls, environment: str) -> "SecurityConfig":
        """
        Create security configuration for specific environment.
        
        Args:
            environment: Environment name (development, testing, staging, production)
            
        Returns:
            SecurityConfig instance optimized for the environment
        """
        try:
            security_level = SecurityLevel(environment.lower())
        except ValueError:
            security_level = SecurityLevel.PRODUCTION
        
        config = cls()
        config.security_level = security_level
        
        if security_level == SecurityLevel.DEVELOPMENT:
            config._apply_development_settings()
        elif security_level == SecurityLevel.TESTING:
            config._apply_testing_settings()
        elif security_level == SecurityLevel.STAGING:
            config._apply_staging_settings()
        else:  # PRODUCTION
            config._apply_production_settings()
        
        return config
    
    def _apply_development_settings(self):
        """Apply development-specific security settings."""
        # Relaxed security for development
        self.enable_introspection = True
        self.enable_playground = True
        self.enable_debug_mode = True
        
        # More permissive limits
        self.query_complexity.maximum_complexity = 200
        self.query_depth.max_depth = 20
        self.rate_limiting.rate_limit = 1000
        
        # Disable error masking for debugging
        self.error_masking.mask_errors_in_production = False
        
        # Verbose logging
        self.security_logging.log_all_operations = True
        self.security_logging.log_level = LogLevel.DEBUG
        
        # Relaxed CSRF for development
        self.csrf_protection.enabled = False
    
    def _apply_testing_settings(self):
        """Apply testing-specific security settings."""
        # Similar to development but with some production features
        self.enable_introspection = True
        self.enable_playground = False
        self.enable_debug_mode = False
        
        # Moderate limits for testing
        self.query_complexity.maximum_complexity = 150
        self.query_depth.max_depth = 18
        self.rate_limiting.rate_limit = 500
        
        # Enable error masking
        self.error_masking.mask_errors_in_production = True
        
        # Moderate logging
        self.security_logging.log_all_operations = False
        self.security_logging.log_level = LogLevel.INFO
        
        # Enable CSRF protection
        self.csrf_protection.enabled = True
    
    def _apply_staging_settings(self):
        """Apply staging-specific security settings."""
        # Close to production settings
        self.enable_introspection = False
        self.enable_playground = False
        self.enable_debug_mode = False
        
        # Production-like limits
        self.query_complexity.maximum_complexity = 100
        self.query_depth.max_depth = 15
        self.rate_limiting.rate_limit = 200
        
        # Enable all security features
        self.error_masking.mask_errors_in_production = True
        
        # Standard logging
        self.security_logging.log_all_operations = False
        self.security_logging.log_level = LogLevel.INFO
        
        # Full CSRF protection
        self.csrf_protection.enabled = True
    
    def _apply_production_settings(self):
        """Apply production-specific security settings."""
        # Maximum security
        self.enable_introspection = False
        self.enable_playground = False
        self.enable_debug_mode = False
        
        # Strict limits
        self.query_complexity.maximum_complexity = 100
        self.query_depth.max_depth = 15
        self.rate_limiting.rate_limit = 100
        
        # Full error masking
        self.error_masking.mask_errors_in_production = True
        
        # Production logging
        self.security_logging.log_all_operations = False
        self.security_logging.log_level = LogLevel.WARNING
        
        # Full security
        self.csrf_protection.enabled = True
    
    def load_from_environment(self) -> "SecurityConfig":
        """
        Load configuration values from environment variables.
        
        Returns:
            Self for method chaining
        """
        # Query complexity
        if os.getenv("GRAPHQL_MAX_COMPLEXITY"):
            self.query_complexity.maximum_complexity = int(os.getenv("GRAPHQL_MAX_COMPLEXITY"))
        
        # Query depth
        if os.getenv("GRAPHQL_MAX_DEPTH"):
            self.query_depth.max_depth = int(os.getenv("GRAPHQL_MAX_DEPTH"))
        
        # Rate limiting
        if os.getenv("GRAPHQL_RATE_LIMIT"):
            self.rate_limiting.rate_limit = int(os.getenv("GRAPHQL_RATE_LIMIT"))
        
        if os.getenv("GRAPHQL_RATE_LIMIT_WINDOW"):
            self.rate_limiting.time_window = int(os.getenv("GRAPHQL_RATE_LIMIT_WINDOW"))
        
        # Security features
        if os.getenv("GRAPHQL_ENABLE_INTROSPECTION"):
            self.enable_introspection = os.getenv("GRAPHQL_ENABLE_INTROSPECTION").lower() == "true"
        
        if os.getenv("GRAPHQL_ENABLE_PLAYGROUND"):
            self.enable_playground = os.getenv("GRAPHQL_ENABLE_PLAYGROUND").lower() == "true"
        
        if os.getenv("GRAPHQL_DEBUG_MODE"):
            self.enable_debug_mode = os.getenv("GRAPHQL_DEBUG_MODE").lower() == "true"
        
        # Error masking
        if os.getenv("GRAPHQL_MASK_ERRORS"):
            self.error_masking.mask_errors_in_production = os.getenv("GRAPHQL_MASK_ERRORS").lower() == "true"
        
        # CSRF protection
        if os.getenv("GRAPHQL_CSRF_ENABLED"):
            self.csrf_protection.enabled = os.getenv("GRAPHQL_CSRF_ENABLED").lower() == "true"
        
        # Trusted origins for CSRF
        if os.getenv("GRAPHQL_TRUSTED_ORIGINS"):
            origins = os.getenv("GRAPHQL_TRUSTED_ORIGINS").split(",")
            self.csrf_protection.trusted_origins = {origin.strip() for origin in origins}
        
        return self
    
    def validate(self) -> List[str]:
        """
        Validate the security configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate complexity limits
        if self.query_complexity.maximum_complexity <= 0:
            errors.append("Query complexity maximum must be positive")
        
        if self.query_depth.max_depth <= 0:
            errors.append("Query depth maximum must be positive")
        
        # Validate rate limiting
        if self.rate_limiting.rate_limit <= 0:
            errors.append("Rate limit must be positive")
        
        if self.rate_limiting.time_window <= 0:
            errors.append("Rate limit time window must be positive")
        
        if self.rate_limiting.burst_limit <= 0:
            errors.append("Burst limit must be positive")
        
        # Validate input sanitization
        if self.input_sanitization.max_string_length <= 0:
            errors.append("Maximum string length must be positive")
        
        # Security warnings for production
        if self.security_level == SecurityLevel.PRODUCTION:
            if self.enable_introspection:
                errors.append("Introspection should be disabled in production")
            
            if self.enable_playground:
                errors.append("GraphQL playground should be disabled in production")
            
            if self.enable_debug_mode:
                errors.append("Debug mode should be disabled in production")
            
            if not self.error_masking.mask_errors_in_production:
                errors.append("Error masking should be enabled in production")
        
        return errors
    
    def get_extension_config(self) -> Dict[str, Any]:
        """
        Get configuration for GraphQL extensions.
        
        Returns:
            Dictionary of extension configurations
        """
        return {
            "query_complexity": {
                "enabled": self.query_complexity.enabled,
                "maximum_complexity": self.query_complexity.maximum_complexity,
                "introspection_complexity": self.query_complexity.introspection_complexity,
                "list_multiplier": self.query_complexity.list_multiplier,
                "connection_multiplier": self.query_complexity.connection_multiplier,
                "enable_logging": self.query_complexity.enable_logging
            },
            "query_depth": {
                "enabled": self.query_depth.enabled,
                "max_depth": self.query_depth.max_depth,
                "enable_logging": self.query_depth.enable_logging
            },
            "rate_limiting": {
                "enabled": self.rate_limiting.enabled,
                "rate_limit": self.rate_limiting.rate_limit,
                "time_window": self.rate_limiting.time_window,
                "burst_limit": self.rate_limiting.burst_limit,
                "enable_logging": self.rate_limiting.enable_logging
            },
            "error_masking": {
                "enabled": self.error_masking.enabled,
                "mask_errors_in_production": self.error_masking.mask_errors_in_production,
                "allowed_error_types": self.error_masking.allowed_error_types,
                "enable_logging": self.error_masking.enable_logging
            },
            "security_logging": {
                "enabled": self.security_logging.enabled,
                "log_all_operations": self.security_logging.log_all_operations,
                "log_introspection": self.security_logging.log_introspection,
                "log_failed_operations": self.security_logging.log_failed_operations,
                "sensitive_fields": self.security_logging.sensitive_fields
            },
            "input_sanitization": {
                "enabled": self.input_sanitization.enabled,
                "enable_html_sanitization": self.input_sanitization.enable_html_sanitization,
                "enable_sql_injection_detection": self.input_sanitization.enable_sql_injection_detection,
                "enable_script_detection": self.input_sanitization.enable_script_detection,
                "max_string_length": self.input_sanitization.max_string_length
            }
        }


# Global security configuration instance
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """
    Get the global security configuration instance.
    
    Returns:
        SecurityConfig instance
    """
    global _security_config
    if _security_config is None:
        # Determine environment from environment variable
        environment = os.getenv("ENVIRONMENT", "production")
        _security_config = SecurityConfig.for_environment(environment)
        _security_config.load_from_environment()
    
    return _security_config


def set_security_config(config: SecurityConfig):
    """
    Set the global security configuration instance.
    
    Args:
        config: SecurityConfig instance to use globally
    """
    global _security_config
    _security_config = config


def reset_security_config():
    """Reset the global security configuration (useful for testing)."""
    global _security_config
    _security_config = None 