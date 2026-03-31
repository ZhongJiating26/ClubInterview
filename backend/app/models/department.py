from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class Department(BaseModel, table=True):
    """
    社团部门表
    """
    __tablename__ = "department"

    club_id: int = Field(
        nullable=False,
        description="所属社团ID"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="部门名称"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="部门描述"
    )
