"""
Security utilities including salted SHA-256 masking and token generation.
"""

import hashlib
import hmac
import json
import secrets
from typing import Dict, Any, Optional
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


def generate_transaction_signature(payload: Dict[str, Any], secret_key: Optional[str] = None) -> str:
    """Generates HMAC-SHA256 state signature for cryptographic ledger blocks."""
    key = (secret_key or settings.SECRET_KEY).encode("utf-8")
    message = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def verify_transaction_signature(
    payload: Dict[str, Any], signature: str, secret_key: Optional[str] = None
) -> bool:
    """Verifies HMAC-SHA256 state signature with timing-attack resistant comparison."""
    expected = generate_transaction_signature(payload, secret_key)
    return hmac.compare_digest(expected, signature)

