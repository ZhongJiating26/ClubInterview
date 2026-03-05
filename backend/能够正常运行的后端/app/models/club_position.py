from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class ClubPosition(BaseModel, table=True):
    """
    社团岗位表（基础岗位定义）
    """
    __tablename__ = "club_position"

    club_id: int = Field(
        nullable=False,
        description="所属社团ID"
    )

    department_id: Optional[int] = Field(
        default=None,
        description="所属部门ID"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="岗位名称"
    )

    description: Optional[str] = Field(
        default=None,
        description="岗位描述"
    )

    requirement: Optional[str] = Field(
        default=None,
        description="任职要求"
    )
