from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class RecruitmentSession(BaseModel, table=True):
    """
    招新场次表
    """
    __tablename__ = "recruitment_session"

    club_id: int = Field(
        nullable=False,
        description="所属社团ID"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="招新场次名称（如：2025秋季招新）"
    )

    description: Optional[str] = Field(
        default=None,
        description="招新说明"
    )

    start_time: datetime = Field(
        nullable=False,
        description="报名开始时间"
    )

    end_time: datetime = Field(
        nullable=False,
        description="报名截止时间"
    )

    max_candidates: Optional[int] = Field(
        default=None,
        description="报名上限人数"
    )

    status: str = Field(
        max_length=20,
        default="DRAFT",
        description="状态：DRAFT / PUBLISHED / CLOSED"
    )

    created_by: Optional[int] = Field(
        default=None,
        description="创建人（社团管理员ID）"
    )
