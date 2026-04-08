from datetime import datetime
from typing import Optional

from sqlmodel import Field

from app.models.base import BaseModel


class InterviewerInvitation(BaseModel, table=True):
    """
    面试官邀请表
    """
    __tablename__ = "interviewer_invitation"

    club_id: int = Field(nullable=False, index=True, description="社团ID")
    user_id: int = Field(nullable=False, index=True, description="被邀请用户ID")
    invite_code: str = Field(
        max_length=50,
        nullable=False,
        unique=True,
        description="邀请编码",
    )
    status: str = Field(
        default="PENDING",
        max_length=20,
        description="状态：PENDING / ACCEPTED / REJECTED / EXPIRED",
    )
    expired_at: Optional[datetime] = Field(default=None, description="过期时间")
    inviter_id: Optional[int] = Field(default=None, description="邀请人用户ID")
