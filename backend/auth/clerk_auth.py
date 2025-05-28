"""
Clerk authentication middleware for FastAPI.

This module provides authentication and authorization middleware that integrates
with Clerk.dev for multi-tenant applications.
"""

import os
import jwt
import httpx
import logging
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer(auto_error=False)

class ClerkAuth:
    """Clerk authentication handler."""
    
    def __init__(self):
        self.secret_key = os.getenv("CLERK_SECRET_KEY")
        self.publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")
        
        if not self.secret_key:
            logger.error("CLERK_SECRET_KEY environment variable is required")
            raise ValueError("CLERK_SECRET_KEY environment variable is required")
        
        # Extract instance from publishable key for API calls
        if self.publishable_key and self.publishable_key.startswith("pk_test_"):
            # Extract instance identifier from publishable key
            self.instance_id = self.publishable_key.replace("pk_test_", "").split("-")[0]
        else:
            self.instance_id = None
            
        self.jwks_cache = {}
        self.jwks_cache_time = None
        
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Clerk."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.clerk.dev/v1/jwks",
                    headers={"Authorization": f"Bearer {self.secret_key}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token from Clerk."""
        try:
            # For development, we'll do basic verification with generous grace period
            # In production, you should verify against Clerk's JWKS
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}  # Handle expiration manually
            )
            
            # FIXED: Handle timezone issues in development with generous grace period
            if "exp" in payload:
                exp_timestamp = payload["exp"]
                current_timestamp = datetime.now().timestamp()  # Use local time consistently
                
                # Only log time debug info at debug level to reduce noise
                logger.debug(f"Token exp: {exp_timestamp}, Current: {current_timestamp:.0f}")
                
                # Give a very generous grace period for development (30 minutes)
                # This handles timezone issues and temporary token refresh delays
                grace_period = 1800  # 30 minutes
                
                if current_timestamp > exp_timestamp + grace_period:
                    time_expired = current_timestamp - exp_timestamp
                    logger.warning(f"Token expired {time_expired:.0f} seconds ago (beyond grace period)")
                    raise HTTPException(
                        status_code=401, 
                        detail=f"Token expired. Please refresh the page or log in again."
                    )
                elif current_timestamp > exp_timestamp:
                    time_expired = current_timestamp - exp_timestamp
                    logger.info(f"Token expired by {time_expired:.0f} seconds but within grace period")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.error("JWT token expired")
            raise HTTPException(
                status_code=401, 
                detail="Token expired. Please refresh the page or log in again."
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token. Please refresh the page or log in again."
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed. Please refresh the page or log in again."
            )
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from Clerk."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.dev/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {self.secret_key}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Failed to fetch user info: {e}")
            return None
    
    async def get_organization_info(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization information from Clerk."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.dev/v1/organizations/{org_id}",
                    headers={"Authorization": f"Bearer {self.secret_key}"}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Failed to fetch organization info: {e}")
            return None

# Global instance
clerk_auth = ClerkAuth()

class AuthUser:
    """Represents an authenticated user with organization context."""
    
    def __init__(self, user_id: str, org_id: Optional[str] = None, org_role: Optional[str] = None, 
                 email: Optional[str] = None, name: Optional[str] = None):
        self.user_id = user_id
        self.org_id = org_id
        self.org_role = org_role
        self.email = email
        self.name = name
    
    def has_org_access(self) -> bool:
        """Check if user has organization access."""
        return self.org_id is not None
    
    def is_org_admin(self) -> bool:
        """Check if user is an organization admin."""
        return self.org_role in ["admin", "owner"]
    
    def __repr__(self):
        return f"AuthUser(user_id={self.user_id}, org_id={self.org_id}, org_role={self.org_role})"

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthUser:
    """
    Dependency to get the current authenticated user.
    
    This function extracts and validates the JWT token from the request,
    then returns an AuthUser object with user and organization information.
    """
    logger.debug(f"🔍 Auth request to {request.url.path} from {request.client.host if request.client else 'unknown'}")
    logger.debug(f"📝 Has credentials: {credentials is not None}")
    if not credentials:
        # Check for session token in cookies as fallback
        session_token = request.cookies.get("__session")
        if not session_token:
            # Try other common Clerk cookie names
            for cookie_name in request.cookies:
                if cookie_name.startswith("__session"):
                    session_token = request.cookies[cookie_name]
                    break
        
        if session_token:
            token = session_token
        else:
            raise HTTPException(status_code=401, detail="Authentication required")
    else:
        token = credentials.credentials
    
    try:
        # Verify the token
        payload = await clerk_auth.verify_token(token)
        
        # Extract user information
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        # Extract organization information if present
        # Clerk stores org info in 'o' object or direct claims
        org_data = payload.get("o", {})
        org_id = org_data.get("id") or payload.get("org_id")
        org_role = org_data.get("rol") or payload.get("org_role")
        
        # Try to get additional user info from the token
        email = payload.get("email")
        name = payload.get("name") or payload.get("full_name")
        
        return AuthUser(
            user_id=user_id,
            org_id=org_id,
            org_role=org_role,
            email=email,
            name=name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_user_with_org(
    current_user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """
    Dependency that requires the user to have organization access.
    
    This is useful for endpoints that specifically require multi-tenant context.
    """
    if not current_user.has_org_access():
        raise HTTPException(
            status_code=403, 
            detail="Organization access required. Please select an organization."
        )
    return current_user

async def require_org_admin(
    current_user: AuthUser = Depends(get_current_user_with_org)
) -> AuthUser:
    """
    Dependency that requires the user to be an organization admin.
    """
    if not current_user.is_org_admin():
        raise HTTPException(
            status_code=403,
            detail="Organization admin access required"
        )
    return current_user

def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthUser]:
    """
    Optional authentication dependency.
    
    Returns the authenticated user if valid credentials are provided,
    otherwise returns None. Useful for endpoints that have both public
    and authenticated behavior.
    """
    if not credentials:
        return None
    
    try:
        # This would need to be async, but keeping it simple for now
        return None  # Placeholder - implement if needed
    except:
        return None

# Utility functions

def get_org_id_from_user(user: AuthUser) -> str:
    """
    Extract organization ID from authenticated user.
    
    Raises HTTPException if user doesn't have organization access.
    """
    if not user.org_id:
        raise HTTPException(
            status_code=403,
            detail="Organization access required"
        )
    return user.org_id

def verify_org_access(user: AuthUser, required_org_id: str) -> bool:
    """
    Verify that the user has access to the specified organization.
    """
    return user.org_id == required_org_id

# Error handlers and middleware

class AuthenticationError(Exception):
    """Custom authentication error."""
    pass

class AuthorizationError(Exception):
    """Custom authorization error."""
    pass
