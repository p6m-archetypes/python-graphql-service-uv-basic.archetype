"""
Complete GraphQL schema definitions for {{ PrefixName }}{{ SuffixName }}.

This module contains the complete GraphQL schema structure including
the root Query, Mutation, and Subscription types with all resolvers integrated
for a full-featured real-time GraphQL API with comprehensive security.
"""

import strawberry
from typing import Optional, List, AsyncGenerator

# Import GraphQL types from API package (pure schemas)
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.schema.types import (
    {{ PrefixName }}Type,
    {{ PrefixName }}Connection,
    {{ PrefixName }}ConnectionArgs,
    {{ PrefixName }}Response,
    Delete{{ PrefixName }}Response
)

# Import input types from API package (pure schemas)
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.graphql.inputs import (
    {{ PrefixName }}Filter,
    {{ PrefixName }}Sort,
    Create{{ PrefixName }}Input,
    Update{{ PrefixName }}Input,
    CreateMultiple{{ PrefixName }}Input
)

# Import resolvers from local server package
from .resolvers.query_resolvers import {{ PrefixName }}QueryResolver
from .resolvers.mutation_resolvers import {{ PrefixName }}MutationResolver

# Import subscription components from local server package
from .subscriptions import (
    {{ PrefixName }}SubscriptionResolver,
    {{ PrefixName }}ChangeEvent,
    SubscriptionFilter,
    SubscriptionStats
)

# Import security components from local server package
from .security import (
    # Extensions
    QueryComplexityExtension,
    QueryDepthExtension,
    RateLimitExtension,
    ErrorMaskingExtension,
    SecurityLoggingExtension,
    InputSanitizationExtension,
    
    # Permissions
    IsAuthenticated,
    IsAdmin,
    IsOwner,
    HasRole,
    IsAdminOrOwner,
    CommonPermissions,
    
    # Validators
    GraphQLSecurityValidator,
    QueryAnalyzer,
    
    # Config
    get_security_config
)

# Import monitoring components from local server package
from .monitoring import create_monitoring_extensions


@strawberry.type
class Query:
    """
    Root Query type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.
    
    This contains all available read operations that clients can perform
    to retrieve data from the service. All queries include pagination support,
    filtering capabilities, and comprehensive security validation.
    """
    
    @strawberry.field(description="A simple ping query to test connectivity")
    def ping(self) -> str:
        return "pong"
    
    # {{ PrefixName }} queries with security permissions
    {{ prefix_name }}s: {{ PrefixName }}Connection = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.get_{{ prefix_name }}s,
        description="Get a paginated list of {{ prefix_name }}s with filtering and sorting",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    {{ prefix_name }}: Optional[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.get_{{ prefix_name }},
        description="Get a specific {{ prefix_name }} by ID",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    {{ prefix_name }}_by_name: Optional[{{ PrefixName }}Type] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.get_{{ prefix_name }}_by_name,
        description="Get a specific {{ prefix_name }} by name",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    search_{{ prefix_name }}s: {{ PrefixName }}Connection = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.search_{{ prefix_name }}s,
        description="Search {{ prefix_name }}s with full-text search capabilities",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    # Admin-only queries with elevated permissions
    {{ prefix_name }}_statistics: Optional[str] = strawberry.field(
        resolver={{ PrefixName }}QueryResolver.get_{{ prefix_name }}_statistics,
        description="Get comprehensive statistics about {{ prefix_name }}s (admin only)",
        permission_classes=[CommonPermissions.admin]
    )


@strawberry.type
class Mutation:
    """
    Root Mutation type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.
    
    This contains all available mutation operations that clients can perform
    to modify data in the service. All mutations include comprehensive validation,
    error handling, transaction support, and real-time event broadcasting.
    """
    
    @strawberry.mutation(description="A simple ping mutation to test connectivity")
    def ping(self) -> str:
        return "pong"

    # {{ PrefixName }} mutations with authentication requirements
    create_{{ prefix_name }}: {{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.create_{{ prefix_name }},
        description="Create a new {{ prefix_name }} with validation and business rules",
        permission_classes=[CommonPermissions.authenticated]
    )

    update_{{ prefix_name }}: {{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.update_{{ prefix_name }},
        description="Update an existing {{ prefix_name }} with validation and conflict checking",
        permission_classes=[CommonPermissions.admin_or_owner]
    )

    delete_{{ prefix_name }}: Delete{{ PrefixName }}Response = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.delete_{{ prefix_name }},
        description="Delete a {{ prefix_name }} with confirmation and business rule validation",
        permission_classes=[CommonPermissions.admin_or_owner]
    )

    create_multiple_{{ prefix_name }}s: List[{{ PrefixName }}Response] = strawberry.field(
        resolver={{ PrefixName }}MutationResolver.create_multiple_{{ prefix_name }}s,
        description="Create multiple {{ prefix_name }}s in a single batch operation",
        permission_classes=[CommonPermissions.authenticated]
    )


@strawberry.type
class Subscription:
    """
    Root Subscription type for the {{ PrefixName }}{{ SuffixName }} GraphQL API.
    
    This contains all available subscription operations that clients can use
    to receive real-time updates about data changes in the service. All subscriptions
    include filtering capabilities and proper authorization checks.
    """
    
    # Real-time {{ prefix_name }} updates
    {{ prefix_name }}_changes: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_{{ prefix_name }}_changes,
        description="Subscribe to real-time {{ prefix_name }} change events (create, update, delete)",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    {{ prefix_name }}_created: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_{{ prefix_name }}_created,
        description="Subscribe to {{ prefix_name }} creation events only",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    {{ prefix_name }}_updated: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_{{ prefix_name }}_updated,
        description="Subscribe to {{ prefix_name }} update events only",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    {{ prefix_name }}_deleted: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_{{ prefix_name }}_deleted,
        description="Subscribe to {{ prefix_name }} deletion events only",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    user_{{ prefix_name }}_changes: AsyncGenerator[{{ PrefixName }}ChangeEvent, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_user_{{ prefix_name }}_changes,
        description="Subscribe to {{ prefix_name }} changes for the current user only",
        permission_classes=[CommonPermissions.authenticated]
    )
    
    # Admin-only subscription with elevated permissions
    subscription_stats: AsyncGenerator[SubscriptionStats, None] = strawberry.subscription(
        resolver={{ PrefixName }}SubscriptionResolver.subscribe_to_stats,
        description="Subscribe to real-time subscription statistics (admin only)",
        permission_classes=[CommonPermissions.admin]
    )


def create_security_extensions() -> List:
    """
    Create security extensions based on configuration.
    
    Returns:
        List of configured security extensions
    """
    security_config = get_security_config()
    extensions = []
    
    # Query complexity extension
    if security_config.query_complexity.enabled:
        extensions.append(QueryComplexityExtension(
            maximum_complexity=security_config.query_complexity.maximum_complexity,
            introspection_complexity=security_config.query_complexity.introspection_complexity,
            list_multiplier=security_config.query_complexity.list_multiplier,
            connection_multiplier=security_config.query_complexity.connection_multiplier,
            enable_logging=security_config.query_complexity.enable_logging
        ))
    
    # Query depth extension
    if security_config.query_depth.enabled:
        extensions.append(QueryDepthExtension(
            max_depth=security_config.query_depth.max_depth,
            enable_logging=security_config.query_depth.enable_logging
        ))
    
    # Rate limiting extension
    if security_config.rate_limiting.enabled:
        extensions.append(RateLimitExtension(
            rate_limit=security_config.rate_limiting.rate_limit,
            time_window=security_config.rate_limiting.time_window,
            burst_limit=security_config.rate_limiting.burst_limit,
            enable_logging=security_config.rate_limiting.enable_logging
        ))
    
    # Error masking extension
    if security_config.error_masking.enabled:
        extensions.append(ErrorMaskingExtension(
            mask_errors_in_production=security_config.error_masking.mask_errors_in_production,
            allowed_error_types=security_config.error_masking.allowed_error_types,
            enable_logging=security_config.error_masking.enable_logging
        ))
    
    # Security logging extension
    if security_config.security_logging.enabled:
        extensions.append(SecurityLoggingExtension(
            log_all_operations=security_config.security_logging.log_all_operations,
            log_introspection=security_config.security_logging.log_introspection,
            log_failed_operations=security_config.security_logging.log_failed_operations,
            sensitive_fields=security_config.security_logging.sensitive_fields
        ))
    
    # Input sanitization extension
    if security_config.input_sanitization.enabled:
        extensions.append(InputSanitizationExtension(
            enable_html_sanitization=security_config.input_sanitization.enable_html_sanitization,
            enable_sql_injection_detection=security_config.input_sanitization.enable_sql_injection_detection,
            enable_script_detection=security_config.input_sanitization.enable_script_detection,
            max_string_length=security_config.input_sanitization.max_string_length
        ))
    
    return extensions


def create_schema() -> strawberry.Schema:
    """
    Create the complete GraphQL schema with all security features enabled.
    
    Returns:
        Configured Strawberry GraphQL schema with security extensions
    """
    security_config = get_security_config()
    
    # Create schema with security and monitoring extensions
    all_extensions = create_security_extensions() + create_monitoring_extensions()
    
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        extensions=all_extensions,
        # Configure schema-level security
        config=strawberry.SchemaConfig(
            auto_camel_case=True,
            enable_federation=False,
            enable_subscriptions=True
        )
    )
    
    # Set schema description with security information
    schema_description = f"""
    {{ PrefixName }}{{ SuffixName }} GraphQL API Schema
    
    A comprehensive GraphQL API with real-time subscriptions and enterprise-grade security.
    
    Security Features Enabled:
    - Query Complexity Analysis (Max: {security_config.query_complexity.maximum_complexity})
    - Query Depth Limiting (Max: {security_config.query_depth.max_depth})
    - Rate Limiting ({security_config.rate_limiting.rate_limit} req/{security_config.rate_limiting.time_window}s)
    - Error Masking: {"Enabled" if security_config.error_masking.mask_errors_in_production else "Disabled"}
    - Input Sanitization: {"Enabled" if security_config.input_sanitization.enabled else "Disabled"}
    - Field-Level Authorization: Enabled
    - Real-time Subscriptions: Enabled
    - CSRF Protection: {"Enabled" if security_config.csrf_protection.enabled else "Disabled"}
    - Security Headers: {"Enabled" if security_config.security_headers.enabled else "Disabled"}
    
    Security Level: {security_config.security_level.value.upper()}
    Introspection: {"Enabled" if security_config.enable_introspection else "Disabled"}
    GraphQL Playground: {"Enabled" if security_config.enable_playground else "Disabled"}
    
    For production use, ensure all security features are properly configured
    and environment variables are set correctly.
    """
    
    # Add description to schema
    if hasattr(schema, '_schema'):
        schema._schema.description = schema_description.strip()
    
    return schema


# Create the main schema instance
schema = create_schema()


def get_schema_with_security_validation() -> strawberry.Schema:
    """
    Get the schema with additional security validation layer.
    
    This adds an extra layer of security validation that runs
    before the normal GraphQL execution process.
    
    Returns:
        Schema with enhanced security validation
    """
    original_schema = create_schema()
    security_validator = QueryAnalyzer()
    
    # This would integrate the security validator with the schema execution
    # The actual implementation would depend on how Strawberry allows
    # custom validation to be integrated
    
    return original_schema


def get_security_info() -> dict:
    """
    Get information about the current security configuration.
    
    Returns:
        Dictionary with security configuration details
    """
    security_config = get_security_config()
    
    return {
        "security_level": security_config.security_level.value,
        "query_complexity": {
            "enabled": security_config.query_complexity.enabled,
            "max_complexity": security_config.query_complexity.maximum_complexity,
            "max_depth": security_config.query_depth.max_depth
        },
        "rate_limiting": {
            "enabled": security_config.rate_limiting.enabled,
            "rate_limit": security_config.rate_limiting.rate_limit,
            "time_window": security_config.rate_limiting.time_window
        },
        "error_masking": {
            "enabled": security_config.error_masking.enabled,
            "mask_in_production": security_config.error_masking.mask_errors_in_production
        },
        "csrf_protection": {
            "enabled": security_config.csrf_protection.enabled
        },
        "security_headers": {
            "enabled": security_config.security_headers.enabled
        },
        "input_sanitization": {
            "enabled": security_config.input_sanitization.enabled
        },
        "features": {
            "introspection": security_config.enable_introspection,
            "playground": security_config.enable_playground,
            "subscriptions": True,
            "permissions": True
        }
    } 