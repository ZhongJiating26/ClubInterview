from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class InterviewSessionScoreItem(BaseModel, table=True):
    """
    面试场次-评分项关联表
    """
    __tablename__ = "interview_session_score_item"

    session_id: int = Field(
        nullable=False,
        description="面试场次ID"
    )

    score_item_id: int = Field(
        nullable=False,
        description="评分项ID"
    )

    order_no: int = Field(
        nullable=False,
        description="排序"
    )
