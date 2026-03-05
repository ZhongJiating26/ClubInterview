from datetime import datetime, timedelta
from typing import Any, Dict
from datetime import datetime, timezone
from jose import jwt, JWTError

from app.core.config import settings


def create_access_token(
    *,
    subject: Dict[str, Any],
    expires_minutes: int | None = None,
) -> str:
    if expires_minutes is None:
        expires_minutes = settings.jwt_expire_minutes

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)

    payload = subject.copy()
    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    解码并校验 access token
    仅做：
    - 签名校验
    - 过期校验
    不做：
    - 数据库查询
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
