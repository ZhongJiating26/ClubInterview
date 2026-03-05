from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class InterviewCandidate(BaseModel, table=True):
    """
    候选人排期表
    """
    __tablename__ = "interview_candidate"

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
        description="用户ID"
    )

    planned_start_time: Optional[datetime] = Field(
        default=None,
        description="计划开始时间"
    )

    planned_end_time: Optional[datetime] = Field(
        default=None,
        description="计划结束时间"
    )

    actual_start_time: Optional[datetime] = Field(
        default=None,
        description="实际开始时间"
    )

    actual_end_time: Optional[datetime] = Field(
        default=None,
        description="实际结束时间"
    )

    status: str = Field(
        max_length=20,
        default="PENDING",
        description="状态：PENDING / IN_PROGRESS / COMPLETED / CANCELLED"
    )

    final_score: Optional[float] = Field(
        default=None,
        description="最终面试得分"
    )
