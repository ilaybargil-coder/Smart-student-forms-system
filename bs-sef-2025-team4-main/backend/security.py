# backend/security.py
import os
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# ✅ עדיף לשים ב-.env: JWT_SECRET_KEY=...
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# bcrypt מגביל את הסיסמה ל-72 bytes
BCRYPT_MAX_BYTES = 72


def _password_bytes(password: str) -> bytes:
    if password is None:
        raise ValueError("Password is required")
    return password.encode("utf-8")


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    ⚠️ bcrypt has a hard limit of 72 BYTES (not chars).
    We enforce it to avoid silent truncation.
    """
    pwd_bytes = _password_bytes(password)
    if len(pwd_bytes) > BCRYPT_MAX_BYTES:
        raise ValueError("Password too long (bcrypt max is 72 bytes).")

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored bcrypt hash."""
    if not password_hash:
        return False

    pwd_bytes = _password_bytes(password)
    if len(pwd_bytes) > BCRYPT_MAX_BYTES:
        # אם הסיסמה ארוכה מדי - בוודאות לא תתאים
        return False

    try:
        return bcrypt.checkpw(pwd_bytes, password_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token with expiration."""
    to_encode = dict(data)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token. Returns payload or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None