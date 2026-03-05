from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class AdmissionResult(BaseModel, table=True):
    """
    录取结果表
    """
    __tablename__ = "admission_result"

    interview_candidate_id: Optional[int] = Field(
        default=None,
        description="候选人排期记录ID"
    )

    signup_session_id: Optional[int] = Field(
        default=None,
        description="报名主表ID"
    )

    candidate_user_id: int = Field(
        nullable=False,
        description="候选人用户ID"
    )

    department_id: Optional[int] = Field(
        default=None,
        description="录取所属部门ID"
    )

    position_id: Optional[int] = Field(
        default=None,
        description="录取岗位ID"
    )

    result: str = Field(
        max_length=20,
        default="PENDING",
        description="录取结果：PENDING / PASS / REJECT / WAITLIST"
    )

    final_score_snapshot: Optional[float] = Field(
        default=None,
        description="用于决策的最终得分快照"
    )

    decided_by: Optional[int] = Field(
        default=None,
        description="录取决策人ID（通常为社团管理员）"
    )

    decided_at: Optional[datetime] = Field(
        default=None,
        description="做出录取决策的时间"
    )

    remark: Optional[str] = Field(
        default=None,
        max_length=255,
        description="备注（例如淘汰原因）"
    )
