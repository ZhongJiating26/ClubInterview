from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class InterviewRecord(BaseModel, table=True):
    """
    面试记录表
    """
    __tablename__ = "interview_record"

    session_id: int = Field(
        nullable=False,
        description="场次ID"
    )

    signup_session_id: Optional[int] = Field(
        default=None,
        description="报名ID"
    )

    candidate_user_id: int = Field(
        nullable=False,
        description="学生ID"
    )

    interviewer_id: int = Field(
        nullable=False,
        description="面试官ID"
    )

    status: str = Field(
        max_length=20,
        default="PENDING",
        description="状态：PENDING / SCORED"
    )

    total_score: Optional[float] = Field(
        default=None,
        description="总分"
    )

    summary: Optional[str] = Field(
        default=None,
        description="总结"
    )

    record_text: Optional[str] = Field(
        default=None,
        description="手写记录"
    )

    recording_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="录音URL"
    )

    face_image_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="照片URL"
    )

    transcript_status: str = Field(
        max_length=20,
        default="PENDING",
        description="转写状态：PENDING / PROCESSING / DONE / FAILED"
    )

    transcript_text: Optional[str] = Field(
        default=None,
        description="转写内容"
    )
