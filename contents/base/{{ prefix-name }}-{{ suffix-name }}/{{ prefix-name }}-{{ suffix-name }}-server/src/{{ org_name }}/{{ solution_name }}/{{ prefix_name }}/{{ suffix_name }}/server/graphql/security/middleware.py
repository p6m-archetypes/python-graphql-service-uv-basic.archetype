"""
Security middleware for {{ PrefixName }}{{ SuffixName }} GraphQL API.

This module provides middleware components for CSRF protection,
security headers, and other security-related HTTP-level protections.
"""

import logging
import secrets
import time
from typing import Dict, Set, Optional, Callable, Any
from urllib.parse import urlparse

from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import get_security_config

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for Cross-Site Request Forgery (CSRF) protection.
    
    Validates CSRF tokens for GraphQL mutations and other state-changing operations
    to prevent CSRF attacks against the GraphQL endpoint.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        csrf_header_name: str = "X-CSRF-Token",
        csrf_cookie_name: str = "csrf_token",
        trusted_origins: Optional[Set[str]] = None,
        require_csrf_for_queries: bool = False
    ):
        """
        Initialize CSRF protection middleware.
        
        Args:
            app: ASGI application
            csrf_header_name: Header name for CSRF token
            csrf_cookie_name: Cookie name for CSRF token
            trusted_origins: Set of trusted origins that bypass CSRF checks
            require_csrf_for_queries: Whether to require CSRF tokens for queries too
        """
        super().__init__(app)
        self.csrf_header_name = csrf_header_name
        self.csrf_cookie_name = csrf_cookie_name
        self.trusted_origins = trusted_origins or set()
        self.require_csrf_for_queries = require_csrf_for_queries
        self.token_cache: Dict[str, float] = {}  # token -> expiry time
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through CSRF protection."""
        security_config = get_security_config()
        
        # Skip CSRF protection if disabled
        if not security_config.csrf_protection.enabled:
            return await call_next(request)
        
        # Skip for non-GraphQL endpoints or safe methods
        if not self._should_check_csrf(request):
            return await call_next(request)
        
        # Check if origin is trusted
        if self._is_trusted_origin(request):
            return await call_next(request)
        
        # Generate CSRF token for GET requests (to set up protection)
        if request.method == "GET":
            response = await call_next(request)
            self._set_csrf_token(response)
            return response
        
        # Validate CSRF token for POST requests
        if request.method == "POST":
            if not self._validate_csrf_token(request):
                logger.warning(
                    "CSRF validation failed",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "origin": request.headers.get("origin"),
                        "referer": request.headers.get("referer"),
                        "user_agent": request.headers.get("user-agent")
                    }
                )
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token validation failed"
                )
        
        return await call_next(request)
    
    def _should_check_csrf(self, request: Request) -> bool:
        """Determine if CSRF protection should be applied to this request."""
        # Check if this is a GraphQL endpoint
        path = request.url.path
        graphql_paths = ["/graphql", "/api/graphql", "/v1/graphql"]
        
        if not any(path.startswith(gql_path) for gql_path in graphql_paths):
            return False
        
        # Only check POST requests (mutations) unless configured otherwise
        if request.method == "GET" and not self.require_csrf_for_queries:
            return False
        
        return True
    
    def _is_trusted_origin(self, request: Request) -> bool:
        """Check if the request origin is in the trusted list."""
        origin = request.headers.get("origin")
        if not origin:
            return False
        
        # Parse origin to get just the domain
        try:
            parsed_origin = urlparse(origin)
            origin_domain = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
            return origin_domain in self.trusted_origins
        except:
            return False
    
    def _validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token from request headers and cookies."""
        # Get token from header
        header_token = request.headers.get(self.csrf_header_name)
        if not header_token:
            return False
        
        # Get token from cookie
        cookie_token = request.cookies.get(self.csrf_cookie_name)
        if not cookie_token:
            return False
        
        # Tokens must match
        if header_token != cookie_token:
            return False
        
        # Check if token is in our cache and not expired
        current_time = time.time()
        if header_token in self.token_cache:
            expiry_time = self.token_cache[header_token]
            if current_time < expiry_time:
                return True
            else:
                # Token expired, remove from cache
                del self.token_cache[header_token]
        
        return False
    
    def _set_csrf_token(self, response: Response):
        """Set CSRF token in response cookie."""
        # Generate new token
        token = secrets.token_urlsafe(32)
        
        # Set expiry (1 hour from now)
        expiry_time = time.time() + 3600
        self.token_cache[token] = expiry_time
        
        # Clean up expired tokens
        current_time = time.time()
        expired_tokens = [t for t, exp in self.token_cache.items() if exp < current_time]
        for expired_token in expired_tokens:
            del self.token_cache[expired_token]
        
        # Set cookie
        response.set_cookie(
            key=self.csrf_cookie_name,
            value=token,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=True,  # HTTPS only
            samesite="strict"
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to all responses.
    
    Adds comprehensive security headers to protect against various
    web-based attacks and improve the security posture of the API.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        content_security_policy: Optional[str] = None,
        x_frame_options: str = "DENY",
        x_content_type_options: str = "nosniff",
        x_xss_protection: str = "1; mode=block",
        strict_transport_security: Optional[str] = None,
        referrer_policy: str = "strict-origin-when-cross-origin"
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            content_security_policy: CSP header value
            x_frame_options: X-Frame-Options header value
            x_content_type_options: X-Content-Type-Options header value
            x_xss_protection: X-XSS-Protection header value
            strict_transport_security: HSTS header value
            referrer_policy: Referrer-Policy header value
        """
        super().__init__(app)
        self.content_security_policy = content_security_policy
        self.x_frame_options = x_frame_options
        self.x_content_type_options = x_content_type_options
        self.x_xss_protection = x_xss_protection
        self.strict_transport_security = strict_transport_security
        self.referrer_policy = referrer_policy
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        security_config = get_security_config()
        
        # Skip if security headers are disabled
        if not security_config.security_headers.enabled:
            return response
        
        # Add security headers
        headers_config = security_config.security_headers
        
        if headers_config.content_security_policy:
            response.headers["Content-Security-Policy"] = headers_config.content_security_policy
        
        if headers_config.x_frame_options:
            response.headers["X-Frame-Options"] = headers_config.x_frame_options
        
        if headers_config.x_content_type_options:
            response.headers["X-Content-Type-Options"] = headers_config.x_content_type_options
        
        if headers_config.x_xss_protection:
            response.headers["X-XSS-Protection"] = headers_config.x_xss_protection
        
        if headers_config.strict_transport_security and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = headers_config.strict_transport_security
        
        if headers_config.referrer_policy:
            response.headers["Referrer-Policy"] = headers_config.referrer_policy
        
        # Additional security headers
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        
        return response


class GraphQLSecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive GraphQL security middleware that combines multiple protections.
    
    This middleware provides a unified security layer for GraphQL operations,
    including request validation, security logging, and threat detection.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        enable_logging: bool = True,
        blocked_user_agents: Optional[Set[str]] = None,
        rate_limit_whitelist: Optional[Set[str]] = None
    ):
        """
        Initialize GraphQL security middleware.
        
        Args:
            app: ASGI application
            enable_logging: Whether to enable security logging
            blocked_user_agents: Set of user agent patterns to block
            rate_limit_whitelist: Set of IPs to exempt from rate limiting
        """
        super().__init__(app)
        self.enable_logging = enable_logging
        self.blocked_user_agents = blocked_user_agents or {
            "scanner", "bot", "crawler", "spider", "scraper"
        }
        self.rate_limit_whitelist = rate_limit_whitelist or set()
        
        # Security metrics
        self.blocked_requests = 0
        self.suspicious_requests = 0
        self.total_requests = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through GraphQL security checks."""
        self.total_requests += 1
        start_time = time.time()
        
        # Check if this is a GraphQL request
        if not self._is_graphql_request(request):
            return await call_next(request)
        
        # Security checks
        security_check_result = self._perform_security_checks(request)
        if not security_check_result["allowed"]:
            self.blocked_requests += 1
            
            if self.enable_logging:
                logger.warning(
                    f"GraphQL request blocked: {security_check_result['reason']}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "user_agent": request.headers.get("user-agent"),
                        "origin": request.headers.get("origin"),
                        "reason": security_check_result["reason"]
                    }
                )
            
            raise HTTPException(
                status_code=403,
                detail=security_check_result["reason"]
            )
        
        # Log suspicious but allowed requests
        if security_check_result.get("suspicious", False):
            self.suspicious_requests += 1
            
            if self.enable_logging:
                logger.info(
                    f"Suspicious GraphQL request: {security_check_result.get('warning', 'Unknown')}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "user_agent": request.headers.get("user-agent"),
                        "warning": security_check_result.get("warning")
                    }
                )
        
        # Process request
        response = await call_next(request)
        
        # Log successful request
        if self.enable_logging:
            execution_time = (time.time() - start_time) * 1000  # milliseconds
            logger.debug(
                "GraphQL request completed",
                extra={
                    "client_ip": request.client.host if request.client else "unknown",
                    "execution_time_ms": execution_time,
                    "status_code": response.status_code
                }
            )
        
        return response
    
    def _is_graphql_request(self, request: Request) -> bool:
        """Check if this is a GraphQL request."""
        path = request.url.path.lower()
        return any(graphql_path in path for graphql_path in ["/graphql", "/api/graphql"])
    
    def _perform_security_checks(self, request: Request) -> Dict[str, Any]:
        """Perform comprehensive security checks on the request."""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Check user agent blocking
        for blocked_pattern in self.blocked_user_agents:
            if blocked_pattern.lower() in user_agent:
                return {
                    "allowed": False,
                    "reason": f"Blocked user agent pattern: {blocked_pattern}"
                }
        
        # Check for suspicious patterns
        suspicious_warnings = []
        
        # Check for automation tools
        automation_indicators = [
            "curl", "wget", "python-requests", "postman", "insomnia",
            "httpie", "node-fetch", "axios"
        ]
        
        for indicator in automation_indicators:
            if indicator in user_agent:
                suspicious_warnings.append(f"Automation tool detected: {indicator}")
        
        # Check for known vulnerability scanners
        scanner_patterns = [
            "nmap", "nikto", "sqlmap", "burp", "zap", "w3af", 
            "dirb", "gobuster", "wfuzz", "ffuf"
        ]
        
        for scanner in scanner_patterns:
            if scanner in user_agent:
                return {
                    "allowed": False,
                    "reason": f"Security scanner detected: {scanner}"
                }
        
        # Check request size (potential DoS)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1000000:  # 1MB limit
            return {
                "allowed": False,
                "reason": "Request too large"
            }
        
        # Rate limiting whitelist check
        if client_ip in self.rate_limit_whitelist:
            return {"allowed": True, "whitelisted": True}
        
        # Return result
        result = {"allowed": True}
        
        if suspicious_warnings:
            result["suspicious"] = True
            result["warning"] = "; ".join(suspicious_warnings)
        
        return result
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics for monitoring."""
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "suspicious_requests": self.suspicious_requests,
            "block_rate": self.blocked_requests / max(self.total_requests, 1),
            "suspicious_rate": self.suspicious_requests / max(self.total_requests, 1)
        }


def create_security_middleware_stack() -> list:
    """
    Create a complete stack of security middleware based on configuration.
    
    Returns:
        List of middleware classes configured according to security settings
    """
    security_config = get_security_config()
    middleware_stack = []
    
    # Add security headers middleware
    if security_config.security_headers.enabled:
        middleware_stack.append((
            SecurityHeadersMiddleware,
            {
                "content_security_policy": security_config.security_headers.content_security_policy,
                "x_frame_options": security_config.security_headers.x_frame_options,
                "x_content_type_options": security_config.security_headers.x_content_type_options,
                "x_xss_protection": security_config.security_headers.x_xss_protection,
                "strict_transport_security": security_config.security_headers.strict_transport_security,
                "referrer_policy": security_config.security_headers.referrer_policy
            }
        ))
    
    # Add CSRF protection middleware
    if security_config.csrf_protection.enabled:
        middleware_stack.append((
            CSRFProtectionMiddleware,
            {
                "csrf_header_name": security_config.csrf_protection.csrf_header_name,
                "csrf_cookie_name": security_config.csrf_protection.csrf_cookie_name,
                "trusted_origins": security_config.csrf_protection.trusted_origins,
                "require_csrf_for_queries": False
            }
        ))
    
    # Add GraphQL security middleware
    middleware_stack.append((
        GraphQLSecurityMiddleware,
        {
            "enable_logging": security_config.security_logging.enabled,
            "blocked_user_agents": {"scanner", "bot", "crawler", "spider", "scraper"},
            "rate_limit_whitelist": security_config.rate_limiting.whitelist_ips
        }
    ))
    
    return middleware_stack 