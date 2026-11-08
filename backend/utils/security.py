"""
Security utilities including salted SHA-256 masking and token generation.
"""

import hashlib
import secrets
from backend.config.settings import settings


def hash_sensitive_identifier(raw_id: str, salt: str | None = None) -> str:
    """
    Computes deterministic salted SHA-256 hash for sensitive customer/merchant IDs.
    Guarantees zero plaintext PII leakage in storage or logs.
    """
    active_salt = salt or settings.PII_SECRET_SALT
    salted_str = f"{active_salt}:{raw_id}".encode("utf-8")
    return hashlib.sha256(salted_str).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generates cryptographically random URL-safe token."""
    return secrets.token_urlsafe(length)

