from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text
from pydantic import Field as PydanticField
from pydantic import model_serializer

from app.models.base import BaseModel


class SignupSession(BaseModel, table=True):
    """
    报名主表（一个学生一次招新活动）
    """
    __tablename__ = "signup_session"

    user_id: int = Field(
        nullable=False,
        description="报名人ID"
    )

    recruitment_session_id: int = Field(
        nullable=False,
        description="招新场次ID"
    )

    self_intro: Optional[str] = Field(
        default=None,
        description="自我介绍"
    )

    extra_fields_json: Optional[str] = Field(
        default=None,
        description="其他表单项（JSON格式）"
    )

    status: str = Field(
        max_length=20,
        default="PENDING",
        description="状态：PENDING / APPROVED / REJECTED"
    )

    audit_user_id: Optional[int] = Field(
        default=None,
        description="审核人ID"
    )

    audit_time: Optional[datetime] = Field(
        default=None,
        description="审核时间"
    )

    audit_reason: Optional[str] = Field(
        default=None,
        max_length=255,
        description="拒绝理由"
    )
