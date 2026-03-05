from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class InterviewScore(BaseModel, table=True):
    """
    面试评分明细表
    """
    __tablename__ = "interview_score"

    record_id: int = Field(
        nullable=False,
        description="面试记录ID"
    )

    score_item_id: int = Field(
        nullable=False,
        description="评分项ID"
    )

    item_name: str = Field(
        max_length=100,
        nullable=False,
        description="冗余：项名"
    )

    item_weight: int = Field(
        nullable=False,
        description="冗余：权重"
    )

    item_max_score: float = Field(
        nullable=False,
        description="冗余：满分"
    )

    score: float = Field(
        nullable=False,
        description="得分"
    )

    remark: Optional[str] = Field(
        default=None,
        max_length=255,
        description="备注"
    )
