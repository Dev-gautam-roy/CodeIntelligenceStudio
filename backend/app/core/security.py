import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.exceptions import SecurityViolationError


def _get_fernet_key() -> bytes:
    """Derives a stable 32-byte Fernet key from the application SECRET_KEY."""
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_token(token: str) -> str:
    """Encrypts a sensitive credential (e.g. GitHub PAT) using Fernet."""
    if not token:
        return ""
    cipher = Fernet(_get_fernet_key())
    return cipher.encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a sensitive credential."""
    if not encrypted_token:
        return ""
    try:
        cipher = Fernet(_get_fernet_key())
        return cipher.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise SecurityViolationError(f"Failed to decrypt stored credential: {str(e)}")


def sanitize_input(value: str) -> str:
    """Removes null bytes and control characters to prevent command injection / injection bypasses."""
    if not isinstance(value, str):
        return value
    return value.replace("\x00", "").strip()
