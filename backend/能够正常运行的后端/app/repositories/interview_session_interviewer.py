from typing import List
from sqlmodel import Session, select

from app.models.interview_session_interviewer import InterviewSessionInterviewer
from app.repositories.base import BaseRepository


class InterviewSessionInterviewerRepository(BaseRepository[InterviewSessionInterviewer]):
    """面试场次-面试官关联仓储"""

    def __init__(self):
        super().__init__(InterviewSessionInterviewer)

    def get_by_session(
        self,
        session: Session,
        interview_session_id: int,
    ) -> List[InterviewSessionInterviewer]:
        """
        获取面试场次的所有面试官
        """
        stmt = (
            select(InterviewSessionInterviewer)
            .where(InterviewSessionInterviewer.session_id == interview_session_id)
            .where(InterviewSessionInterviewer.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_interviewer(
        self,
        session: Session,
        interviewer_id: int,
    ) -> List[InterviewSessionInterviewer]:
        """
        获取面试官参与的所有面试场次
        """
        stmt = (
            select(InterviewSessionInterviewer)
            .where(InterviewSessionInterviewer.interviewer_id == interviewer_id)
            .where(InterviewSessionInterviewer.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())

    def add_interviewer(
        self,
        session: Session,
        interview_session_id: int,
        interviewer_id: int,
        role: str = "INTERVIEWER",
    ) -> InterviewSessionInterviewer:
        """
        添加面试官到场次
        """
        # 检查是否已存在
        existing = session.execute(
            select(InterviewSessionInterviewer)
            .where(InterviewSessionInterviewer.session_id == interview_session_id)
            .where(InterviewSessionInterviewer.interviewer_id == interviewer_id)
            .where(InterviewSessionInterviewer.is_deleted == 0)
        ).scalar_one_or_none()

        if existing:
            return existing

        relation = InterviewSessionInterviewer(
            session_id=interview_session_id,
            interviewer_id=interviewer_id,
            role=role,
        )
        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation

    def remove_interviewer(
        self,
        session: Session,
        interview_session_id: int,
        interviewer_id: int,
    ):
        """
        从场次移除面试官
        """
        relation = session.execute(
            select(InterviewSessionInterviewer)
            .where(InterviewSessionInterviewer.session_id == interview_session_id)
            .where(InterviewSessionInterviewer.interviewer_id == interviewer_id)
            .where(InterviewSessionInterviewer.is_deleted == 0)
        ).scalar_one_or_none()

        if relation:
            self.soft_delete(session, relation)
            session.commit()
