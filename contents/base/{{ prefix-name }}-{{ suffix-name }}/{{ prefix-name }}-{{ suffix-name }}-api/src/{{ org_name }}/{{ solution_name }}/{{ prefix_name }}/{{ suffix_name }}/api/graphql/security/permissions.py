"""
GraphQL permission system for {{ PrefixName }}{{ SuffixName }}.

This module provides comprehensive field-level authorization classes
that integrate with Strawberry GraphQL to enforce access control
at the resolver level with role-based and ownership-based permissions.
"""

import logging
from typing import Any, Optional, List, Dict, Set, Union
from abc import ABC, abstractmethod
from enum import Enum

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

# Import context for user information
from ..resolvers.context import ResolverContext

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Enumeration of user roles for permission checking."""
    
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class PermissionResult:
    """Result of a permission check with detailed information."""
    
    def __init__(self, allowed: bool, reason: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.allowed = allowed
        self.reason = reason or ("Permission granted" if allowed else "Permission denied")
        self.details = details or {}
    
    def __bool__(self) -> bool:
        """Allow using PermissionResult as a boolean."""
        return self.allowed


class SecurityPermissionChecker:
    """
    Central permission checker that provides logging and monitoring
    for all permission decisions in the GraphQL API.
    """
    
    def __init__(self, enable_logging: bool = True, log_denials: bool = True):
        self.enable_logging = enable_logging
        self.log_denials = log_denials
        self.permission_checks = 0
        self.permission_denials = 0
    
    def check_permission(
        self, 
        permission_class: str, 
        context: ResolverContext, 
        result: PermissionResult,
        field_name: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> PermissionResult:
        """
        Central method for checking and logging permissions.
        
        Args:
            permission_class: Name of the permission class being checked
            context: Resolver context with user information
            result: Result of the permission check
            field_name: Name of the field being accessed
            resource_id: ID of the resource being accessed
            
        Returns:
            The same PermissionResult with logging applied
        """
        self.permission_checks += 1
        
        if not result.allowed:
            self.permission_denials += 1
            
            if self.log_denials and self.enable_logging:
                logger.warning(
                    f"Permission denied: {permission_class}",
                    extra={
                        "event_type": "permission_denied",
                        "permission_class": permission_class,
                        "user_id": getattr(context, 'user_id', None),
                        "field_name": field_name,
                        "resource_id": resource_id,
                        "reason": result.reason,
                        "client_ip": self._get_client_ip(context)
                    }
                )
        elif self.enable_logging:
            logger.debug(
                f"Permission granted: {permission_class}",
                extra={
                    "event_type": "permission_granted",
                    "permission_class": permission_class,
                    "user_id": getattr(context, 'user_id', None),
                    "field_name": field_name,
                    "resource_id": resource_id
                }
            )
        
        return result
    
    def _get_client_ip(self, context: ResolverContext) -> str:
        """Get client IP from context for logging."""
        try:
            if hasattr(context, 'request') and hasattr(context.request, 'client'):
                return context.request.client.host
        except:
            pass
        return "unknown"
    
    def get_stats(self) -> Dict[str, int]:
        """Get permission checking statistics."""
        return {
            "total_checks": self.permission_checks,
            "total_denials": self.permission_denials,
            "approval_rate": (self.permission_checks - self.permission_denials) / max(self.permission_checks, 1)
        }


# Global permission checker instance
permission_checker = SecurityPermissionChecker()


class IsAuthenticated(BasePermission):
    """
    Permission class that requires user authentication.
    
    This is the most basic permission that checks if a user
    is logged in and has a valid session.
    """
    
    message = "Authentication required. Please log in to access this resource."
    error_extensions = {"code": "AUTHENTICATION_REQUIRED"}
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is authenticated."""
        context: ResolverContext = info.context
        
        result = PermissionResult(
            allowed=context.is_authenticated(),
            reason="User is not authenticated" if not context.is_authenticated() else "User is authenticated"
        )
        
        final_result = permission_checker.check_permission(
            permission_class="IsAuthenticated",
            context=context,
            result=result,
            field_name=info.field_name
        )
        
        return final_result.allowed


class IsAdmin(BasePermission):
    """
    Permission class that requires admin role.
    
    Checks if the authenticated user has admin privileges
    for accessing admin-only resources and operations.
    """
    
    message = "Admin privileges required. This resource is restricted to administrators."
    error_extensions = {"code": "ADMIN_REQUIRED"}
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has admin role."""
        context: ResolverContext = info.context
        
        if not context.is_authenticated():
            result = PermissionResult(
                allowed=False,
                reason="User is not authenticated"
            )
        elif not context.has_role("admin"):
            result = PermissionResult(
                allowed=False,
                reason=f"User {context.user_id} does not have admin role"
            )
        else:
            result = PermissionResult(
                allowed=True,
                reason=f"User {context.user_id} has admin role"
            )
        
        final_result = permission_checker.check_permission(
            permission_class="IsAdmin",
            context=context,
            result=result,
            field_name=info.field_name
        )
        
        return final_result.allowed


class IsOwner(BasePermission):
    """
    Permission class that requires resource ownership.
    
    Checks if the authenticated user owns the resource being accessed.
    This is useful for user-specific data like profiles, settings, etc.
    """
    
    message = "Resource ownership required. You can only access your own resources."
    error_extensions = {"code": "OWNERSHIP_REQUIRED"}
    
    def __init__(self, owner_field: str = "user_id"):
        """
        Initialize ownership permission.
        
        Args:
            owner_field: Field name that contains the owner ID in the source object
        """
        self.owner_field = owner_field
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user owns the resource."""
        context: ResolverContext = info.context
        
        if not context.is_authenticated():
            result = PermissionResult(
                allowed=False,
                reason="User is not authenticated"
            )
        else:
            # Extract owner ID from source object or kwargs
            owner_id = None
            
            if source and hasattr(source, self.owner_field):
                owner_id = getattr(source, self.owner_field)
            elif self.owner_field in kwargs:
                owner_id = kwargs[self.owner_field]
            elif hasattr(source, 'id') and self.owner_field == "id":
                owner_id = source.id
            
            if owner_id is None:
                result = PermissionResult(
                    allowed=False,
                    reason=f"Cannot determine resource owner (field: {self.owner_field})"
                )
            elif str(owner_id) == str(context.user_id):
                result = PermissionResult(
                    allowed=True,
                    reason=f"User {context.user_id} owns resource {owner_id}"
                )
            else:
                result = PermissionResult(
                    allowed=False,
                    reason=f"User {context.user_id} does not own resource {owner_id}"
                )
        
        final_result = permission_checker.check_permission(
            permission_class="IsOwner",
            context=context,
            result=result,
            field_name=info.field_name,
            resource_id=str(owner_id) if owner_id else None
        )
        
        return final_result.allowed


class HasRole(BasePermission):
    """
    Permission class that requires specific role(s).
    
    Flexible permission class that can check for one or more required roles.
    """
    
    def __init__(self, required_roles: Union[str, List[str]], require_all: bool = False):
        """
        Initialize role-based permission.
        
        Args:
            required_roles: Single role or list of roles required
            require_all: If True, user must have ALL roles. If False, user needs ANY role.
        """
        if isinstance(required_roles, str):
            self.required_roles = [required_roles]
        else:
            self.required_roles = required_roles
        
        self.require_all = require_all
        
        # Set dynamic message based on configuration
        if len(self.required_roles) == 1:
            self.message = f"Role '{self.required_roles[0]}' required to access this resource."
        elif self.require_all:
            self.message = f"All roles {self.required_roles} required to access this resource."
        else:
            self.message = f"One of roles {self.required_roles} required to access this resource."
        
        self.error_extensions = {"code": "ROLE_REQUIRED", "required_roles": self.required_roles}
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has required role(s)."""
        context: ResolverContext = info.context
        
        if not context.is_authenticated():
            result = PermissionResult(
                allowed=False,
                reason="User is not authenticated"
            )
        else:
            user_roles = context.get_user_roles()
            
            if self.require_all:
                # User must have ALL required roles
                missing_roles = [role for role in self.required_roles if not context.has_role(role)]
                if missing_roles:
                    result = PermissionResult(
                        allowed=False,
                        reason=f"User {context.user_id} missing required roles: {missing_roles}",
                        details={"user_roles": user_roles, "missing_roles": missing_roles}
                    )
                else:
                    result = PermissionResult(
                        allowed=True,
                        reason=f"User {context.user_id} has all required roles: {self.required_roles}",
                        details={"user_roles": user_roles}
                    )
            else:
                # User needs ANY of the required roles
                matching_roles = [role for role in self.required_roles if context.has_role(role)]
                if matching_roles:
                    result = PermissionResult(
                        allowed=True,
                        reason=f"User {context.user_id} has required role(s): {matching_roles}",
                        details={"user_roles": user_roles, "matching_roles": matching_roles}
                    )
                else:
                    result = PermissionResult(
                        allowed=False,
                        reason=f"User {context.user_id} lacks any required roles: {self.required_roles}",
                        details={"user_roles": user_roles, "required_roles": self.required_roles}
                    )
        
        final_result = permission_checker.check_permission(
            permission_class="HasRole",
            context=context,
            result=result,
            field_name=info.field_name
        )
        
        return final_result.allowed


class IsAdminOrOwner(BasePermission):
    """
    Permission class that requires either admin role OR resource ownership.
    
    This is a common pattern where admins can access any resource,
    but regular users can only access their own resources.
    """
    
    message = "Admin privileges or resource ownership required."
    error_extensions = {"code": "ADMIN_OR_OWNER_REQUIRED"}
    
    def __init__(self, owner_field: str = "user_id"):
        """
        Initialize admin-or-owner permission.
        
        Args:
            owner_field: Field name that contains the owner ID in the source object
        """
        self.owner_field = owner_field
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is admin or owns the resource."""
        context: ResolverContext = info.context
        
        if not context.is_authenticated():
            result = PermissionResult(
                allowed=False,
                reason="User is not authenticated"
            )
        elif context.has_role("admin"):
            result = PermissionResult(
                allowed=True,
                reason=f"User {context.user_id} has admin role"
            )
        else:
            # Check ownership
            owner_id = None
            
            if source and hasattr(source, self.owner_field):
                owner_id = getattr(source, self.owner_field)
            elif self.owner_field in kwargs:
                owner_id = kwargs[self.owner_field]
            elif hasattr(source, 'id') and self.owner_field == "id":
                owner_id = source.id
            
            if owner_id is None:
                result = PermissionResult(
                    allowed=False,
                    reason=f"Cannot determine resource owner (field: {self.owner_field})"
                )
            elif str(owner_id) == str(context.user_id):
                result = PermissionResult(
                    allowed=True,
                    reason=f"User {context.user_id} owns resource {owner_id}"
                )
            else:
                result = PermissionResult(
                    allowed=False,
                    reason=f"User {context.user_id} is not admin and does not own resource {owner_id}"
                )
        
        final_result = permission_checker.check_permission(
            permission_class="IsAdminOrOwner",
            context=context,
            result=result,
            field_name=info.field_name,
            resource_id=str(owner_id) if 'owner_id' in locals() and owner_id else None
        )
        
        return final_result.allowed


class HasPermission(BasePermission):
    """
    Permission class for custom permission checking.
    
    Allows for complex, custom permission logic that can be
    defined per field or operation.
    """
    
    def __init__(
        self, 
        permission_name: str,
        permission_checker_func: Optional[callable] = None,
        error_message: Optional[str] = None
    ):
        """
        Initialize custom permission.
        
        Args:
            permission_name: Name of the permission for logging
            permission_checker_func: Function that checks the permission
            error_message: Custom error message for permission denial
        """
        self.permission_name = permission_name
        self.permission_checker_func = permission_checker_func
        self.message = error_message or f"Permission '{permission_name}' required to access this resource."
        self.error_extensions = {"code": "CUSTOM_PERMISSION_REQUIRED", "permission": permission_name}
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check custom permission."""
        context: ResolverContext = info.context
        
        if not context.is_authenticated():
            result = PermissionResult(
                allowed=False,
                reason="User is not authenticated"
            )
        elif self.permission_checker_func:
            try:
                permission_granted = self.permission_checker_func(context, source, info, **kwargs)
                result = PermissionResult(
                    allowed=permission_granted,
                    reason=f"Custom permission '{self.permission_name}' {'granted' if permission_granted else 'denied'}"
                )
            except Exception as e:
                logger.error(f"Error in custom permission checker '{self.permission_name}': {e}")
                result = PermissionResult(
                    allowed=False,
                    reason=f"Error checking custom permission '{self.permission_name}'"
                )
        else:
            # No checker function provided, default to deny
            result = PermissionResult(
                allowed=False,
                reason=f"No permission checker defined for '{self.permission_name}'"
            )
        
        final_result = permission_checker.check_permission(
            permission_class="HasPermission",
            context=context,
            result=result,
            field_name=info.field_name
        )
        
        return final_result.allowed


# Convenience permission instances for common use cases
class CommonPermissions:
    """Pre-configured permission instances for common scenarios."""
    
    # Authentication permissions
    authenticated = IsAuthenticated()
    admin = IsAdmin()
    
    # Role-based permissions
    moderator = HasRole("moderator")
    admin_or_moderator = HasRole(["admin", "moderator"], require_all=False)
    super_admin = HasRole("super_admin")
    
    # Ownership permissions
    owner = IsOwner()
    admin_or_owner = IsAdminOrOwner()
    
    # Custom permission factories
    @staticmethod
    def require_roles(*roles, require_all: bool = False) -> HasRole:
        """Factory for creating role requirements."""
        return HasRole(list(roles), require_all=require_all)
    
    @staticmethod
    def owner_of(field: str) -> IsOwner:
        """Factory for creating ownership requirements."""
        return IsOwner(owner_field=field)
    
    @staticmethod
    def admin_or_owner_of(field: str) -> IsAdminOrOwner:
        """Factory for creating admin-or-owner requirements."""
        return IsAdminOrOwner(owner_field=field)


def get_permission_stats() -> Dict[str, Any]:
    """Get permission checking statistics for monitoring."""
    return permission_checker.get_stats() 