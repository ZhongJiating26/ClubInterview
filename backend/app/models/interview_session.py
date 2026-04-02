from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class InterviewSession(BaseModel, table=True):
    """
    面试场次表
    """
    __tablename__ = "interview_session"

    club_id: int = Field(
        nullable=False,
        description="社团ID"
    )

    recruitment_session_id: Optional[int] = Field(
        default=None,
        description="招新场次ID"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="场次名称"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="描述"
    )

    place: Optional[str] = Field(
        default=None,
        max_length=255,
        description="面试地点"
    )

    start_time: Optional[datetime] = Field(
        default=None,
        description="开始时间"
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="结束时间"
    )

    status: str = Field(
        max_length=20,
        default="DRAFT",
        description="状态：DRAFT / OPEN / CLOSED"
    )

    created_by: Optional[int] = Field(
        default=None,
        description="创建者用户ID"
    )
