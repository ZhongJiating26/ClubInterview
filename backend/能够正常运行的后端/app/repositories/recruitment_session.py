from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select, and_

from app.models.recruitment_session import RecruitmentSession
from app.models.recruitment_session_position import RecruitmentSessionPosition
from app.repositories.base import BaseRepository


class RecruitmentSessionRepository(BaseRepository[RecruitmentSession]):
    """
    招新场次仓储
    """

    def __init__(self):
        super().__init__(RecruitmentSession)

    def get_all(
        self,
        session: Session,
        include_deleted: bool = False,
    ) -> List[RecruitmentSession]:
        """
        获取所有招新场次
        """
        stmt = select(RecruitmentSession)
        if not include_deleted:
            stmt = stmt.where(RecruitmentSession.is_deleted == 0)
        stmt = stmt.order_by(RecruitmentSession.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_club(
        self,
        session: Session,
        club_id: int,
        status: Optional[str] = None,
    ) -> List[RecruitmentSession]:
        """
        获取社团的招新场次列表
        """
        stmt = (
            select(RecruitmentSession)
            .where(RecruitmentSession.club_id == club_id)
            .where(RecruitmentSession.is_deleted == 0)
        )
        if status:
            stmt = stmt.where(RecruitmentSession.status == status)
        stmt = stmt.order_by(RecruitmentSession.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_active_sessions(
        self,
        session: Session,
        club_id: Optional[int] = None,
    ) -> List[RecruitmentSession]:
        """
        获取当前可报名的场次（PUBLISHED状态且在报名时间内）
        """
        now = datetime.now()
        stmt = (
            select(RecruitmentSession)
            .where(RecruitmentSession.is_deleted == 0)
            .where(RecruitmentSession.status == "PUBLISHED")
            .where(RecruitmentSession.start_time <= now)
            .where(RecruitmentSession.end_time >= now)
        )
        if club_id:
            stmt = stmt.where(RecruitmentSession.club_id == club_id)
        stmt = stmt.order_by(RecruitmentSession.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    def is_registration_open(self, session: Session, session_id: int) -> bool:
        """
        检查招新场次是否在报名时间内
        """
        now = datetime.now()
        stmt = (
            select(RecruitmentSession)
            .where(RecruitmentSession.id == session_id)
            .where(RecruitmentSession.is_deleted == 0)
            .where(RecruitmentSession.status == "PUBLISHED")
            .where(RecruitmentSession.start_time <= now)
            .where(RecruitmentSession.end_time >= now)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none() is not None


class RecruitmentSessionPositionRepository(BaseRepository[RecruitmentSessionPosition]):
    """
    招新场次-岗位关联仓储
    """

    def __init__(self):
        super().__init__(RecruitmentSessionPosition)

    def get_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> List[RecruitmentSessionPosition]:
        """
        获取招新场次关联的所有岗位
        """
        stmt = (
            select(RecruitmentSessionPosition)
            .where(RecruitmentSessionPosition.session_id == session_id)
            .where(RecruitmentSessionPosition.is_deleted == 0)
        )
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_session_and_position(
        self,
        session: Session,
        session_id: int,
        position_id: int,
    ) -> Optional[RecruitmentSessionPosition]:
        """
        检查场次是否已关联某岗位
        """
        stmt = (
            select(RecruitmentSessionPosition)
            .where(RecruitmentSessionPosition.session_id == session_id)
            .where(RecruitmentSessionPosition.position_id == position_id)
            .where(RecruitmentSessionPosition.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_total_quota(self, session: Session, session_id: int) -> int:
        """
        获取招新场次的总招募人数
        """
        positions = self.get_by_session(session, session_id)
        return sum(p.recruit_quota or 0 for p in positions)
