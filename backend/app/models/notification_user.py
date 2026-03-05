from datetime import datetime
from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class NotificationUser(BaseModel, table=True):
    """
    用户通知关联表（每条通知与用户的映射）
    """
    __tablename__ = "notification_user"

    notification_id: int = Field(
        nullable=False,
        description="通知ID"
    )

    user_id: int = Field(
        nullable=False,
        description="用户ID"
    )

    read_status: str = Field(
        max_length=20,
        default="UNREAD",
        description="已读状态：UNREAD / READ"
    )

    read_at: Optional[datetime] = Field(
        default=None,
        description="阅读时间"
    )
