from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class ScoreTemplate(BaseModel, table=True):
    """
    评分模板表
    """
    __tablename__ = "score_template"

    club_id: int = Field(
        nullable=False,
        description="社团ID"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="模板名称"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="描述"
    )

    status: str = Field(
        max_length=20,
        default="ACTIVE",
        description="状态：ACTIVE / INACTIVE"
    )
