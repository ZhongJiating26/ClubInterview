from typing import Optional, List
from sqlmodel import Session, select

from app.models.notification import Notification
from app.models.notification_user import NotificationUser
from app.models.ticket import Ticket, TicketReply
from app.models.faq import FAQ
from app.models.signup_session import SignupSession
from app.models.interview_candidate import InterviewCandidate
from app.models.interview_record import InterviewRecord
from app.models.admission_result import AdmissionResult
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """通知仓储"""

    def __init__(self):
        super().__init__(Notification)

    def get_by_user(
        self,
        session: Session,
        user_id: int,
        unread_only: bool = False,
    ) -> List[Notification]:
        """获取用户的通知列表"""
        # 关联 notification_user 表
        stmt = (
            select(Notification)
            .join(NotificationUser, Notification.id == NotificationUser.notification_id)
            .where(NotificationUser.user_id == user_id)
            .where(Notification.is_deleted == 0)
            .where(NotificationUser.is_deleted == 0)
        )
        if unread_only:
            stmt = stmt.where(NotificationUser.read_status == "UNREAD")

        stmt = stmt.order_by(Notification.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_unread_count(
        self,
        session: Session,
        user_id: int,
    ) -> int:
        """获取用户未读通知数量"""
        stmt = (
            select(NotificationUser)
            .where(NotificationUser.user_id == user_id)
            .where(NotificationUser.read_status == "UNREAD")
            .where(NotificationUser.is_deleted == 0)
        )
        result = session.execute(stmt)
        return len(result.all())

    def mark_as_read(
        self,
        session: Session,
        notification_id: int,
        user_id: int,
    ):
        """标记通知为已读"""
        stmt = (
            select(NotificationUser)
            .where(NotificationUser.notification_id == notification_id)
            .where(NotificationUser.user_id == user_id)
            .where(NotificationUser.is_deleted == 0)
        )
        result = session.execute(stmt)
        notification_user = result.scalar_one_or_none()

        if notification_user and notification_user.read_status == "UNREAD":
            from datetime import datetime
            notification_user.read_status = "READ"
            notification_user.read_at = datetime.now()
            session.add(notification_user)
            session.commit()

    def mark_all_as_read(
        self,
        session: Session,
        user_id: int,
    ):
        """标记所有通知为已读"""
        from datetime import datetime

        stmt = (
            select(NotificationUser)
            .where(NotificationUser.user_id == user_id)
            .where(NotificationUser.read_status == "UNREAD")
            .where(NotificationUser.is_deleted == 0)
        )
        result = session.execute(stmt)
        notification_users = result.scalars().all()

        for nu in notification_users:
            nu.read_status = "READ"
            nu.read_at = datetime.now()
            session.add(nu)

        session.commit()


class TicketRepository(BaseRepository[Ticket]):
    """工单仓储"""

    def __init__(self):
        super().__init__(Ticket)

    def get_by_user(
        self,
        session: Session,
        user_id: int,
    ) -> List[Ticket]:
        """获取用户的工单列表"""
        stmt = (
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .where(Ticket.is_deleted == 0)
        )
        stmt = stmt.order_by(Ticket.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())


class TicketReplyRepository(BaseRepository[TicketReply]):
    """工单回复仓储"""

    def __init__(self):
        super().__init__(TicketReply)

    def get_by_ticket(
        self,
        session: Session,
        ticket_id: int,
    ) -> List[TicketReply]:
        """获取工单的回复列表"""
        stmt = (
            select(TicketReply)
            .where(TicketReply.ticket_id == ticket_id)
            .where(TicketReply.is_deleted == 0)
        )
        stmt = stmt.order_by(TicketReply.created_at.asc())
        result = session.execute(stmt)
        return list(result.scalars().all())


class FAQRepository(BaseRepository[FAQ]):
    """FAQ仓储"""

    def __init__(self):
        super().__init__(FAQ)

    def get_all(
        self,
        session: Session,
        category: Optional[str] = None,
        club_id: Optional[int] = None,
    ) -> List[FAQ]:
        """获取FAQ列表"""
        stmt = select(FAQ).where(FAQ.is_deleted == 0)

        if category:
            stmt = stmt.where(FAQ.category == category)
        if club_id is not None:
            stmt = stmt.where(FAQ.club_id == club_id)

        stmt = stmt.order_by(FAQ.is_pinned.desc(), FAQ.order_no, FAQ.created_at)
        result = session.execute(stmt)
        return list(result.scalars().all())
