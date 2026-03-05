from datetime import datetime
from typing import Optional

from sqlmodel import Field

from app.models.base import BaseModel


class VerificationCode(BaseModel, table=True):
    """
    验证码表
    """
    __tablename__ = "verification_code"

    phone: str = Field(
        max_length=20,
        nullable=False,
        description="手机号",
        index=True,
    )
    scene: str = Field(
        max_length=50,
        nullable=False,
        description="场景：REGISTER / LOGIN",
    )
    code: str = Field(
        max_length=10,
        nullable=False,
        description="验证码",
    )
    expired_at: datetime = Field(
        nullable=False,
        description="过期时间",
    )
    is_used: int = Field(
        default=0,
        nullable=False,
        description="是否已使用：0未使用 1已使用",
    )
