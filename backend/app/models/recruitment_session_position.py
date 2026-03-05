from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class RecruitmentSessionPosition(BaseModel, table=True):
    """
    招新场次-岗位关联表
    """
    __tablename__ = "recruitment_session_position"

    session_id: int = Field(
        nullable=False,
        description="招新场次ID"
    )

    position_id: int = Field(
        nullable=False,
        description="岗位ID"
    )

    position_name: str = Field(
        max_length=100,
        description="冗余岗位名称（防止岗位修改影响历史数据）"
    )

    position_description: Optional[str] = Field(
        default=None,
        description="冗余岗位描述"
    )

    position_requirement: Optional[str] = Field(
        default=None,
        description="冗余岗位要求"
    )

    recruit_quota: Optional[int] = Field(
        default=None,
        description="招新人次"
    )
