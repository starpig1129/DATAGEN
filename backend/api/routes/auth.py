"""Authentication API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Header

# Create router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)


@router.post("/api/auth/verify-token")
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify API token validity.

    This endpoint verifies that the provided token is valid.
    Currently performs basic validation; can be extended to
    verify against external services (e.g., OpenAI API).

    Args:
        authorization: Bearer token in Authorization header.

    Returns:
        Dict with verification status.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )

    # Extract token from Bearer format
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]

    # Basic validation
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

    # Check for OpenAI API key format (sk-...)
    if token.startswith("sk-"):
        # Valid OpenAI API key format
        logger.info("Token format validated: OpenAI API key")
        return {
            "valid": True,
            "token_type": "openai_api_key",
            "message": "Token format is valid"
        }

    # Check for Firecrawl API key format (fc-...)
    if token.startswith("fc-"):
        logger.info("Token format validated: Firecrawl API key")
        return {
            "valid": True,
            "token_type": "firecrawl_api_key",
            "message": "Token format is valid"
        }

    # Check for LangChain API key format (lsv2_pt_...)
    if token.startswith("lsv2_pt_"):
        logger.info("Token format validated: LangChain API key")
        return {
            "valid": True,
            "token_type": "langchain_api_key",
            "message": "Token format is valid"
        }

    # Generic token - accept but warn
    logger.warning("Token format not recognized, accepting as generic token")
    return {
        "valid": True,
        "token_type": "generic",
        "message": "Token accepted (format not recognized)"
    }
