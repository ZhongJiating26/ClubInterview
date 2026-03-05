from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class Notification(BaseModel, table=True):
    """
    通知表
    """
    __tablename__ = "notification"

    type: str = Field(
        max_length=50,
        nullable=False,
        description="通知类型：SYSTEM / SIGNUP / INTERVIEW_SCHEDULE / INTERVIEW_RESULT / TICKET"
    )

    title: str = Field(
        max_length=255,
        nullable=False,
        description="通知标题"
    )

    content: str = Field(
        nullable=False,
        description="通知内容"
    )

    biz_id: Optional[int] = Field(
        default=None,
        description="关联业务数据主键"
    )

    sent_at: Optional[datetime] = Field(
        default=None,
        description="发送时间"
    )

    status: str = Field(
        max_length=20,
        default="PENDING",
        description="状态：PENDING / SENT / FAILED"
    )
