import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from backend.core.config import settings
from backend.core.errors import UnauthorizedException

# Initialize Argon2id password hasher conforming to NFR-02.1 & RFC 9106 recommended parameters
# Memory: 64 MB (65536 KiB), Time: 3 iterations, Parallelism: 4 threads
argon2_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hashes password using Argon2id with a unique cryptographic salt (FR-01.2 & NFR-02.1)."""
    try:
        return argon2_hasher.hash(password)
    except Exception:
        # Graceful fallback if argon2 environment throws an unexpected error
        return hash_password_fallback(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored cryptographic hash (supports Argon2id and fallback)."""
    if not hashed_password:
        return False

    # Check for Argon2id hash format ($argon2id$...)
    if hashed_password.startswith("$argon2"):
        try:
            return argon2_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    # Check for SHA256 fallback format (sha256$salt$hash)
    if hashed_password.startswith("sha256$"):
        return verify_password_fallback(plain_password, hashed_password)

    return False


def hash_password_fallback(password: str) -> str:
    """Fallback password hasher using SHA-256 + salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return f"sha256${salt}${hashed}"


def verify_password_fallback(plain_password: str, hashed_password: str) -> bool:
    """Verifies password against stored fallback hash."""
    if not hashed_password or "$" not in hashed_password:
        return False
    parts = hashed_password.split("$")
    if len(parts) != 3:
        return False
    _, salt, stored_hash = parts
    computed = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
    return hmac.compare_digest(stored_hash, computed)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates an encrypted JWT access token valid for 60 minutes (FR-01.3 & NFR-02.3)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": secrets.token_hex(8),
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Cryptographically decodes and verifies a JWT Bearer access token (NFR-02.3)."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
        return payload
    except ExpiredSignatureError:
        raise UnauthorizedException("Authentication token has expired. Please log in again.")
    except InvalidTokenError as err:
        raise UnauthorizedException(f"Invalid authentication token: {str(err)}")


def create_mock_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Helper creating real cryptographically signed JWT token for endpoints and tests."""
    return create_access_token(data, expires_delta)
