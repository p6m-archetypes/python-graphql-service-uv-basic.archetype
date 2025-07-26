"""
GraphQL resolver context for dependency injection.

This module provides the context object that contains all dependencies
needed by GraphQL resolvers, including repositories, dataloaders, and
other services.
"""

from typing import Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

# Import repositories
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories import (
    {{ PrefixName }}Repository
)

# Import dataloaders
from .dataloader import {{ PrefixName }}DataLoader


@dataclass
class ResolverContext:
    """
    Context object that provides access to all dependencies for GraphQL resolvers.
    
    This context is passed to every resolver function and contains repositories,
    dataloaders, and other services needed for business logic execution.
    """
    
    # Database session
    session: AsyncSession
    
    # Repositories
    {{ prefix_name }}_repository: {{ PrefixName }}Repository
    
    # DataLoaders for efficient data fetching
    {{ prefix_name }}_loader: {{ PrefixName }}DataLoader
    
    # User context (if authentication is needed)
    user_id: Optional[str] = None
    user_roles: Optional[list[str]] = None
    
    @classmethod
    def create(
        cls,
        session: AsyncSession,
        user_id: Optional[str] = None,
        user_roles: Optional[list[str]] = None
    ) -> "ResolverContext":
        """
        Create a new resolver context with initialized dependencies.
        
        Args:
            session: Database session
            user_id: Optional authenticated user ID
            user_roles: Optional user roles for authorization
            
        Returns:
            ResolverContext: Configured context with all dependencies
        """
        # Initialize repositories
        {{ prefix_name }}_repository = {{ PrefixName }}Repository(session)
        
        # Initialize dataloaders
        {{ prefix_name }}_loader = {{ PrefixName }}DataLoader({{ prefix_name }}_repository)
        
        return cls(
            session=session,
            {{ prefix_name }}_repository={{ prefix_name }}_repository,
            {{ prefix_name }}_loader={{ prefix_name }}_loader,
            user_id=user_id,
            user_roles=user_roles or []
        )
    
    def is_authenticated(self) -> bool:
        """Check if there is an authenticated user in the context."""
        return self.user_id is not None
    
    def has_role(self, role: str) -> bool:
        """Check if the authenticated user has a specific role."""
        return role in (self.user_roles or [])
    
    def has_any_role(self, roles: list[str]) -> bool:
        """Check if the authenticated user has any of the specified roles."""
        if not self.user_roles:
            return False
        return any(role in self.user_roles for role in roles)
    
    async def cleanup(self) -> None:
        """
        Cleanup resources held by the context.
        
        This should be called when the GraphQL request is complete
        to properly clean up DataLoaders and other resources.
        """
        # Clear DataLoader caches
        self.{{ prefix_name }}_loader.clear_all()
        
        # Note: Session cleanup is typically handled by the FastAPI dependency injection system


# Dependency injection helper for FastAPI
async def get_resolver_context(
    session: AsyncSession,
    user_id: Optional[str] = None,
    user_roles: Optional[list[str]] = None
) -> ResolverContext:
    """
    Dependency injection helper for creating resolver context in FastAPI.
    
    Args:
        session: Database session from FastAPI dependency
        user_id: Optional user ID from authentication middleware
        user_roles: Optional user roles from authentication middleware
        
    Returns:
        ResolverContext: Configured resolver context
    """
    return ResolverContext.create(
        session=session,
        user_id=user_id,
        user_roles=user_roles
    ) 