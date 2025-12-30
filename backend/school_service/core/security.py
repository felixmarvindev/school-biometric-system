"""Security utilities for authentication and password hashing."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from school_service.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Note: bcrypt has a 72-byte limit. This function validates and handles this limitation.
    
    Args:
        password: Plain text password to hash (must be <= 72 bytes)
    
    Returns:
        Hashed password string
    
    Raises:
        ValueError: If password exceeds 72 bytes or other validation fails
    """
    # Check byte length (bcrypt has a 72-byte limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError("Password cannot be longer than 72 bytes. Please use a shorter password.")
    
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # Catch bcrypt-specific errors and convert to user-friendly messages
        error_msg = str(e)
        if "cannot be longer than 72 bytes" in error_msg.lower():
            raise ValueError("Password cannot be longer than 72 bytes. Please use a shorter password.") from e
        # Re-raise other ValueError exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors from bcrypt/passlib
        error_msg = str(e)
        if "72 bytes" in error_msg or "truncate" in error_msg.lower():
            raise ValueError("Password cannot be longer than 72 bytes. Please use a shorter password.") from e
        # For other errors, wrap in a generic message
        raise ValueError(f"Error hashing password: {error_msg}") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload (typically user_id, email, etc.)
        expires_delta: Optional timedelta for token expiration. 
                      If None, uses ACCESS_TOKEN_EXPIRE_MINUTES from settings
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string to decode
    
    Returns:
        Decoded token payload as dictionary, or None if token is invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - Maximum 72 bytes (bcrypt limitation)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check byte length (bcrypt has a 72-byte limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        return False, "Password cannot be longer than 72 bytes. Please use a shorter password."
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    
    return True, ""

