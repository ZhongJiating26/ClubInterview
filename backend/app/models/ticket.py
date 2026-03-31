from datetime import datetime
from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class Ticket(BaseModel, table=True):
    """
    工单主表
    """
    __tablename__ = "ticket"

    user_id: int = Field(
        nullable=False,
        description="提交人ID"
    )

    club_id: Optional[int] = Field(
        default=None,
        description="关联社团ID（可选）"
    )

    title: str = Field(
        max_length=255,
        nullable=False,
        description="工单标题"
    )

    category: str = Field(
        max_length=50,
        nullable=False,
        description="工单分类"
    )

    content: str = Field(
        nullable=False,
        max_length=2000,
        description="工单内容"
    )

    status: str = Field(
        max_length=20,
        default="OPEN",
        description="状态：OPEN / IN_PROGRESS / RESOLVED / CLOSED"
    )

    priority: str = Field(
        max_length=20,
        default="NORMAL",
        description="优先级：LOW / NORMAL / HIGH / URGENT"
    )

    assignee_id: Optional[int] = Field(
        default=None,
        description="处理人ID"
    )

    resolved_at: Optional[datetime] = Field(
        default=None,
        description="解决时间"
    )


class TicketReply(BaseModel, table=True):
    """
    工单回复表
    """
    __tablename__ = "ticket_reply"

    ticket_id: int = Field(
        nullable=False,
        description="工单ID"
    )

    user_id: int = Field(
        nullable=False,
        description="回复人ID"
    )

    content: str = Field(
        nullable=False,
        max_length=2000,
        description="回复内容"
    )

    is_from_staff: bool = Field(
        nullable=False,
        description="是否来自工作人员"
    )

    attachment_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="附件URL"
    )
