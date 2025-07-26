"""
Configuration management for {{ PrefixName }}{{ SuffixName }} API

This module provides environment-based configuration using Pydantic Settings.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    api_title: str = Field(
        default="{{ PrefixName }}{{ SuffixName }} GraphQL API",
        description="API title for OpenAPI documentation"
    )
    api_description: str = Field(
        default="A modern GraphQL API service built with FastAPI and Strawberry",
        description="API description for OpenAPI documentation"
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )
    api_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server"
    )
    api_port: int = Field(
        default=8080,
        description="Port to bind the API server"
    )
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed headers for CORS"
    )
    
    # GraphQL Configuration
    graphql_endpoint: str = Field(
        default="/graphql",
        description="GraphQL endpoint path"
    )
    graphql_playground_enabled: bool = Field(
        default=True,
        description="Enable GraphQL Playground in development"
    )
    graphql_introspection_enabled: bool = Field(
        default=True,
        description="Enable GraphQL schema introspection"
    )
    graphql_max_query_depth: int = Field(
        default=10,
        description="Maximum allowed query depth"
    )
    graphql_max_query_complexity: int = Field(
        default=50,
        description="Maximum allowed query complexity"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/{{ prefix_name }}_{{ suffix_name }}",
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT token signing"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )
    
    # Redis Configuration
    redis_url: Optional[str] = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and sessions"
    )
    
    # Logging Configuration
    logging_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    logging_format: str = Field(
        default="json",
        description="Logging format (json, text)"
    )
    
    # Management Configuration
    management_enabled: bool = Field(
        default=True,
        description="Enable management endpoints"
    )
    management_port: int = Field(
        default=8080,
        description="Port for management endpoints (same as API for REST service)"
    )
    
    # Metrics Configuration
    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    metrics_prometheus_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics export"
    )
    
    # Development Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload for development"
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.reload


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings() 