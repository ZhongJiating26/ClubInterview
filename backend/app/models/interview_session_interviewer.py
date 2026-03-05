from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class InterviewSessionInterviewer(BaseModel, table=True):
    """
    面试场次-面试官关联表
    """
    __tablename__ = "interview_session_interviewer"

    session_id: int = Field(
        nullable=False,
        description="面试场次ID"
    )

    interviewer_id: int = Field(
        nullable=False,
        description="面试官用户ID"
    )

    role: str = Field(
        max_length=20,
        default="INTERVIEWER",
        description="角色：LEAD（主面试官）/ INTERVIEWER（面试官）/ OBSERVER（观察员）"
    )
