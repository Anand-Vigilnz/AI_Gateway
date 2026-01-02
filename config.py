"""
config.py

Purpose:
    Configuration module that loads environment variables from .env file
    and provides default values for the AI Gateway chat application.
    This version supports scan-then-LLM flow (Rproxy for scanning, OpenAI for LLM).

Author:
    Anand S

Date:
    2025-12-16

Last Modified:
    2025-12-16
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def extract_entity_id_from_api_key(api_key: str) -> Optional[str]:
    """
    Extract entity ID from API key format.
    
    Supports formats:
    - vpsk_live_{entityId}{random} - extracts first 24 hex characters after prefix as entity ID
    - vigil_{entityId}_{random} (legacy format) - extracts entity ID from second part
    
    Parameters
    ----------
    api_key:
        API key string (with or without "Bearer " prefix)
    
    Returns
    -------
    Entity ID (24-character MongoDB ObjectId) or None if invalid format
    """
    if not api_key:
        return None
    
    # Remove "Bearer " prefix if present
    api_key = api_key.replace("Bearer ", "").strip()
    
    if not api_key:
        return None
    
    # Try vpsk_live_ format
    # Format: vpsk_live_{entityId}{random}
    # Entity ID is the first 24 hex characters after "vpsk_live_"
    if api_key.startswith("vpsk_live_"):
        # Get everything after "vpsk_live_"
        after_prefix = api_key[len("vpsk_live_"):]
        
        # Extract first 24 hex characters as entity ID
        if len(after_prefix) >= 24:
            entity_id = after_prefix[:24]
            # Validate it's a 24-character hex string (MongoDB ObjectId)
            if all(c in '0123456789abcdefABCDEF' for c in entity_id):
                return entity_id.lower()  # Return lowercase for consistency
    
    # Try legacy vigil_ format for backward compatibility
    # Format: vigil_{entityId}_{random}
    elif api_key.startswith("vigil_"):
        parts = api_key.split("_")
        if len(parts) >= 3:
            entity_id = parts[1]  # Second part after vigil_ is entity ID
            # Validate it's a 24-character hex string (MongoDB ObjectId)
            if len(entity_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in entity_id):
                return entity_id.lower()  # Return lowercase for consistency
    
    return None


# Rproxy Gateway URL (required for security scanning)
# Default to the production gateway URL if not set in .env
RPROXY_URL: str = os.getenv("RPROXY_URL", "https://devaigw.vigilnz.com/")

# Rproxy Authorization Header (required for Rproxy authentication)
# API key for Rproxy authentication (format: vpsk_live_... or Bearer vpsk_live_...)
RPROXY_AUTH_HEADER: str = os.getenv("RPROXY_AUTH_HEADER", "")

# OpenAI API Key (required for LLM requests)
# Your OpenAI API key for direct LLM access
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Default Model Name (optional)
# Default OpenAI model to use if not specified in UI
# Default: gpt-4o-mini
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# OpenAI API Endpoint
# Can be overridden via environment variable OPENAI_API_URL
OPENAI_API_URL: str = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

# Auto-extract entity ID from Rproxy API key if available
ENTITY_ID: str = os.getenv("ENTITY_ID", "")
if not ENTITY_ID and RPROXY_AUTH_HEADER:
    extracted_id = extract_entity_id_from_api_key(RPROXY_AUTH_HEADER)
    if extracted_id:
        ENTITY_ID = extracted_id

# Ensure RPROXY_URL ends with / for consistency
if RPROXY_URL and not RPROXY_URL.endswith("/"):
    RPROXY_URL = f"{RPROXY_URL}/"

