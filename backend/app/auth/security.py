import hashlib
import secrets
from datetime import timedelta

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

SESSION_LIFETIME = timedelta(minutes=30)


def generate_token() -> str:
    """A random secret for session tokens and sensor API keys."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    # The token is 256 bits of randomness, so a fast unsalted hash is enough.
    return hashlib.sha256(token.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)
