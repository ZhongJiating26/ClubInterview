from typing import Optional, List
from sqlmodel import Session, select, and_

from app.models.interview_session import InterviewSession
from app.models.interview_candidate import InterviewCandidate
from app.models.interview_record import InterviewRecord
from app.models.interview_score import InterviewScore
from app.models.admission_result import AdmissionResult
from app.repositories.base import BaseRepository


class InterviewSessionRepository(BaseRepository[InterviewSession]):
    """面试场次仓储"""

    def __init__(self):
        super().__init__(InterviewSession)

    def get_by_club(
        self,
        session: Session,
        club_id: int,
        status: Optional[str] = None,
    ) -> List[InterviewSession]:
        """获取社团的面试场次列表"""
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.club_id == club_id)
            .where(InterviewSession.is_deleted == 0)
        )
        if status:
            stmt = stmt.where(InterviewSession.status == status)
        stmt = stmt.order_by(InterviewSession.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())


class InterviewCandidateRepository(BaseRepository[InterviewCandidate]):
    """候选人排期仓储"""

    def __init__(self):
        super().__init__(InterviewCandidate)

    def get_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> List[InterviewCandidate]:
        """获取场次的候选人列表"""
        stmt = (
            select(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewCandidate.planned_start_time)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_candidate_and_session(
        self,
        session: Session,
        candidate_user_id: int,
        session_id: int,
    ) -> Optional[InterviewCandidate]:
        """获取候选人在某场次的排期"""
        stmt = (
            select(InterviewCandidate)
            .where(InterviewCandidate.candidate_user_id == candidate_user_id)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_interviewer(
        self,
        session: Session,
        interviewer_id: int,
    ) -> List[InterviewCandidate]:
        """获取分配给某面试官的候选人列表"""
        # 需要通过 interview_record 关联
        stmt = (
            select(InterviewCandidate)
            .join(InterviewRecord, InterviewCandidate.candidate_user_id == InterviewRecord.candidate_user_id)
            .where(InterviewRecord.interviewer_id == interviewer_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewCandidate.planned_start_time)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_candidate_user(
        self,
        session: Session,
        candidate_user_id: int,
    ) -> List[InterviewCandidate]:
        """获取某用户作为候选人的所有排期"""
        stmt = (
            select(InterviewCandidate)
            .where(InterviewCandidate.candidate_user_id == candidate_user_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewCandidate.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    # ============ 面试功能增强 ============

    def get_by_user(
        self,
        session: Session,
        user_id: int,
    ) -> List[InterviewCandidate]:
        """获取某用户的所有候选人排期（别名）"""
        return self.get_by_candidate_user(session, user_id)

    def get_session_stats(
        self,
        session: Session,
        session_id: int,
    ) -> dict:
        """
        获取场次的统计数据

        Returns:
            包含统计数据的字典
        """
        from sqlmodel import func

        # 总候选人数量
        total_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        total_candidates = session.execute(total_stmt).scalar() or 0

        # 已完成数量
        completed_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.status == "COMPLETED")
            .where(InterviewCandidate.is_deleted == 0)
        )
        completed_candidates = session.execute(completed_stmt).scalar() or 0

        # 待定数量
        pending_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.status == "PENDING")
            .where(InterviewCandidate.is_deleted == 0)
        )
        pending_candidates = session.execute(pending_stmt).scalar() or 0

        # 取消数量
        cancelled_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.status == "CANCELLED")
            .where(InterviewCandidate.is_deleted == 0)
        )
        cancelled_candidates = session.execute(cancelled_stmt).scalar() or 0

        # 计算平均分
        avg_score_stmt = (
            select(func.avg(InterviewCandidate.final_score))
            .select_from(InterviewCandidate)
            .where(InterviewCandidate.session_id == session_id)
            .where(InterviewCandidate.final_score.is_not(None))
            .where(InterviewCandidate.is_deleted == 0)
        )
        avg_score = session.execute(avg_score_stmt).scalar()

        # 录取结果统计
        from app.models.admission_result import AdmissionResult

        # 通过 JOIN interview_candidate 来获取结果
        pass_count_stmt = (
            select(func.count())
            .select_from(AdmissionResult)
            .join(InterviewCandidate, AdmissionResult.interview_candidate_id == InterviewCandidate.id)
            .where(InterviewCandidate.session_id == session_id)
            .where(AdmissionResult.result == "PASS")
            .where(AdmissionResult.is_deleted == 0)
        )
        pass_count = session.execute(pass_count_stmt).scalar() or 0

        reject_count_stmt = (
            select(func.count())
            .select_from(AdmissionResult)
            .join(InterviewCandidate, AdmissionResult.interview_candidate_id == InterviewCandidate.id)
            .where(InterviewCandidate.session_id == session_id)
            .where(AdmissionResult.result == "REJECT")
            .where(AdmissionResult.is_deleted == 0)
        )
        reject_count = session.execute(reject_count_stmt).scalar() or 0

        waitlist_count_stmt = (
            select(func.count())
            .select_from(AdmissionResult)
            .join(InterviewCandidate, AdmissionResult.interview_candidate_id == InterviewCandidate.id)
            .where(InterviewCandidate.session_id == session_id)
            .where(AdmissionResult.result == "WAITLIST")
            .where(AdmissionResult.is_deleted == 0)
        )
        waitlist_count = session.execute(waitlist_count_stmt).scalar() or 0

        return {
            "total_candidates": total_candidates,
            "completed_candidates": completed_candidates,
            "pending_candidates": pending_candidates,
            "cancelled_candidates": cancelled_candidates,
            "average_score": round(avg_score, 2) if avg_score else None,
            "pass_count": pass_count,
            "reject_count": reject_count,
            "waitlist_count": waitlist_count,
        }


class InterviewRecordRepository(BaseRepository[InterviewRecord]):
    """面试记录仓储"""

    def __init__(self):
        super().__init__(InterviewRecord)

    def get_by_candidate(
        self,
        session: Session,
        candidate_id: int,
    ) -> List[InterviewRecord]:
        """通过候选人ID获取面试记录"""
        # 先获取候选人信息
        candidate = session.execute(
            select(InterviewCandidate).where(InterviewCandidate.id == candidate_id)
        ).scalar_one_or_none()
        if not candidate:
            return []
        # 通过 session_id 和 candidate_user_id 获取记录
        return self.get_by_session_and_candidate(
            session, candidate.session_id, candidate.candidate_user_id
        )

    def get_by_session_and_candidate(
        self,
        session: Session,
        session_id: int,
        candidate_user_id: int,
    ) -> List[InterviewRecord]:
        """获取某场次某候选人的所有面试记录"""
        stmt = (
            select(InterviewRecord)
            .where(InterviewRecord.session_id == session_id)
            .where(InterviewRecord.candidate_user_id == candidate_user_id)
            .where(InterviewRecord.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewRecord.created_at)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_interviewer(
        self,
        session: Session,
        interviewer_id: int,
    ) -> List[InterviewRecord]:
        """获取面试官的所有面试记录"""
        stmt = (
            select(InterviewRecord)
            .where(InterviewRecord.interviewer_id == interviewer_id)
            .where(InterviewRecord.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewRecord.created_at.desc())
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_session_and_interviewer(
        self,
        session: Session,
        session_id: int,
        interviewer_id: int,
    ) -> List[InterviewRecord]:
        """获取某场次某面试官的面试记录"""
        stmt = (
            select(InterviewRecord)
            .where(InterviewRecord.session_id == session_id)
            .where(InterviewRecord.interviewer_id == interviewer_id)
            .where(InterviewRecord.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewRecord.created_at)
        result = session.execute(stmt)
        return list(result.scalars().all())

    # ============ 面试功能增强 ============

    def get_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> List[InterviewRecord]:
        """获取某场次的所有面试记录"""
        stmt = (
            select(InterviewRecord)
            .where(InterviewRecord.session_id == session_id)
            .where(InterviewRecord.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewRecord.created_at)
        result = session.execute(stmt)
        return list(result.scalars().all())


class InterviewScoreRepository(BaseRepository[InterviewScore]):
    """面试评分仓储"""

    def __init__(self):
        super().__init__(InterviewScore)

    def get_by_record(
        self,
        session: Session,
        record_id: int,
    ) -> List[InterviewScore]:
        """获取某面试记录的所有评分"""
        stmt = (
            select(InterviewScore)
            .where(InterviewScore.record_id == record_id)
            .where(InterviewScore.is_deleted == 0)
        )
        stmt = stmt.order_by(InterviewScore.created_at)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def calculate_total_score(
        self,
        session: Session,
        record_id: int,
    ) -> Optional[float]:
        """计算面试记录的总分"""
        scores = self.get_by_record(session, record_id)
        if not scores:
            return None

        # 加权总分计算
        total_weight = sum(s.item_weight for s in scores)
        if total_weight == 0:
            return None

        weighted_sum = sum(s.score * s.item_weight for s in scores)
        return round(weighted_sum / total_weight, 2)


class AdmissionResultRepository(BaseRepository[AdmissionResult]):
    """录取结果仓储"""

    def __init__(self):
        super().__init__(AdmissionResult)

    def get_by_candidate(
        self,
        session: Session,
        candidate_user_id: int,
    ) -> Optional[AdmissionResult]:
        """获取某候选人的录取结果"""
        stmt = (
            select(AdmissionResult)
            .where(AdmissionResult.candidate_user_id == candidate_user_id)
            .where(AdmissionResult.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> List[AdmissionResult]:
        """获取某场次的所有录取结果"""
        # 通过 interview_candidate 关联
        stmt = (
            select(AdmissionResult)
            .join(InterviewCandidate, AdmissionResult.interview_candidate_id == InterviewCandidate.id)
            .where(InterviewCandidate.session_id == session_id)
            .where(AdmissionResult.is_deleted == 0)
        )
        result = session.execute(stmt)
        return list(result.scalars().all())
