import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 48

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> tuple[str, int]:
    """Возвращает (токен, срок жизни в секундах)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=TOKEN_TTL_HOURS)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, TOKEN_TTL_HOURS * 3600


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])