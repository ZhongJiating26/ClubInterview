from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class Role(BaseModel, table=True):
    """
    角色表
    角色编码：ADMIN（系统管理员）/ CLUB_ADMIN（社团管理员）/ INTERVIEWER（面试官）/ STUDENT（普通学生）
    """
    __tablename__ = "role"

    code: str = Field(
        max_length=50,
        nullable=False,
        unique=True,
        description="角色编码"
    )
    name: str = Field(
        max_length=50,
        nullable=False,
        description="角色名称"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="角色描述"
    )