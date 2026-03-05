from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class UserRole(BaseModel, table=True):
    """
    用户角色关联表
    支持一个用户拥有多个角色（例如既是社团管理员又是面试官）
    对于普通学生角色（STUDENT），club_id可以为空
    """
    __tablename__ = "user_role"

    user_id: int = Field(
        nullable=False,
        description="用户ID",
        index=True,
    )
    role_id: int = Field(
        nullable=False,
        description="角色ID",
        index=True,
    )
    club_id: Optional[int] = Field(
        default=None,
        description="所属社团ID（面试官/管理角色特有）",
    )