from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import Session, select, and_, func

from app.models.signup_session import SignupSession
from app.models.signup_item import SignupItem
from app.models.signup_attachment import SignupAttachment
from app.repositories.base import BaseRepository


class SignupSessionRepository(BaseRepository[SignupSession]):
    """
    报名主表仓储
    """

    def __init__(self):
        super().__init__(SignupSession)

    def get_by_user(
        self,
        session: Session,
        user_id: int,
    ) -> List[SignupSession]:
        """
        获取用户的报名列表
        """
        stmt = (
            select(SignupSession)
            .where(SignupSession.user_id == user_id)
            .where(SignupSession.is_deleted == 0)
            .order_by(SignupSession.created_at.desc())
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_user_and_session(
        self,
        session: Session,
        user_id: int,
        recruitment_session_id: int,
    ) -> Optional[SignupSession]:
        """
        检查用户是否已报名某招新场次（未删除的）
        """
        stmt = (
            select(SignupSession)
            .where(SignupSession.user_id == user_id)
            .where(SignupSession.recruitment_session_id == recruitment_session_id)
            .where(SignupSession.is_deleted == 0)
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_by_session(
        self,
        session: Session,
        recruitment_session_id: int,
        status: Optional[str] = None,
    ) -> List[SignupSession]:
        """
        获取某招新场次的报名列表（管理端）
        """
        stmt = (
            select(SignupSession)
            .where(SignupSession.recruitment_session_id == recruitment_session_id)
            .where(SignupSession.is_deleted == 0)
        )
        if status:
            stmt = stmt.where(SignupSession.status == status)
        stmt = stmt.order_by(SignupSession.created_at.desc())
        return list(session.execute(stmt).scalars().all())

    def get_by_recruitment_session(
        self,
        session: Session,
        recruitment_session_id: int,
    ) -> List[SignupSession]:
        """
        获取某招新场次的报名列表（别名）
        """
        return self.get_by_session(session, recruitment_session_id)

    def get_stats_by_session(
        self,
        session: Session,
        recruitment_session_id: int,
    ) -> Dict[str, int]:
        """
        获取某招新场次的报名统计
        返回各状态的报名数量
        """
        stmt = (
            select(
                SignupSession.status,
                func.count(SignupSession.id),
            )
            .where(SignupSession.recruitment_session_id == recruitment_session_id)
            .where(SignupSession.is_deleted == 0)
            .group_by(SignupSession.status)
        )
        results = session.execute(stmt).all()

        stats = {
            "PENDING": 0,
            "APPROVED": 0,
            "REJECTED": 0,
        }
        for status, count in results:
            if status in stats:
                stats[status] = count

        # 计算总数
        stats["total"] = stats["PENDING"] + stats["APPROVED"] + stats["REJECTED"]

        return stats


class SignupItemRepository(BaseRepository[SignupItem]):
    """
    报名子表仓储
    """

    def __init__(self):
        super().__init__(SignupItem)

    def get_by_session(self, session: Session, signup_session_id: int) -> List[SignupItem]:
        """
        获取报名记录的所有岗位选择
        """
        stmt = (
            select(SignupItem)
            .where(SignupItem.signup_session_id == signup_session_id)
            .where(SignupItem.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())


class SignupAttachmentRepository(BaseRepository[SignupAttachment]):
    """
    报名附件仓储
    """

    def __init__(self):
        super().__init__(SignupAttachment)

    def get_by_session(self, session: Session, signup_session_id: int) -> List[SignupAttachment]:
        """
        获取报名记录的所有附件
        """
        stmt = (
            select(SignupAttachment)
            .where(SignupAttachment.signup_session_id == signup_session_id)
            .where(SignupAttachment.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())
