"""Authentication routes."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import extract_user_from_token

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


class TokenVerificationRequest(BaseModel):
    """Token verification request model."""
    token: str


class TokenVerificationResponse(BaseModel):
    """Token verification response model."""
    valid: bool
    user: Dict[str, Any] | None = None
    error: str | None = None


@router.post("/verify", response_model=TokenVerificationResponse)
async def verify_token(
    request: TokenVerificationRequest,
) -> TokenVerificationResponse:
    """Verify JWT token and return user information."""
    try:
        user = extract_user_from_token(request.token)
        if user:
            logger.info("Token verified successfully", user_id=user.get("user_id"))
            return TokenVerificationResponse(valid=True, user=user)
        else:
            logger.warning("Invalid token provided")
            return TokenVerificationResponse(
                valid=False,
                error="Invalid or expired token",
            )
    except Exception as e:
        logger.error("Token verification error", error=str(e))
        return TokenVerificationResponse(
            valid=False,
            error="Token verification failed",
        )


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current user information from JWT token."""
    try:
        user = extract_user_from_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info("User authenticated", user_id=user.get("user_id"))
        return {
            "user_id": user.get("user_id"),
            "email": user.get("email"),
            "role": user.get("role"),
        }
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/config")
async def get_auth_config() -> Dict[str, Any]:
    """Get authentication configuration for frontend."""
    return {
        "supabase_configured": settings.has_supabase_config,
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key": settings.SUPABASE_ANON_KEY,
    }
