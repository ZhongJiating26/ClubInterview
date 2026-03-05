from typing import Optional
from datetime import datetime

from sqlmodel import Field

from app.models.base import BaseModel


class UserAccount(BaseModel, table=True):
    """
    用户账号表
    """
    __tablename__ = "user_account"

    # ===== 基本账号信息 =====
    phone: str = Field(
        max_length=20,
        nullable=False,
        description="手机号"
    )

    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        description="密码哈希"
    )

    token_version: int = Field(
        default=0,
        nullable=False,
        description="Token版本号，用于强制登出/吊销JWT"
    )

    status: int = Field(
        default=1,
        nullable=False,
        description="状态：1正常 0禁用"
    )

    # ===== 个人信息 =====
    name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="姓名"
    )

    id_card_no: Optional[str] = Field(
        default=None,
        max_length=32,
        description="身份证号"
    )

    school_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="所属学校标识码"
    )

    major: Optional[str] = Field(
        default=None,
        max_length=100,
        description="专业"
    )

    student_no: Optional[str] = Field(
        default=None,
        max_length=50,
        description="学号"
    )

    avatar_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="头像URL"
    )

    email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="邮箱"
    )

    is_verified_campus: int = Field(
        default=0,
        nullable=False,
        description="校园认证是否通过：1是 0否"
    )

    last_login_at: Optional[datetime] = Field(
        default=None,
        description="最近登录时间"
    )
