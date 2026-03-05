from typing import List

from sqlmodel import Session, select

from app.models.interview_session_score_item import InterviewSessionScoreItem
from app.repositories.base import BaseRepository


class InterviewSessionScoreItemRepository(BaseRepository[InterviewSessionScoreItem]):
    """面试场次-评分项关联仓储"""

    def __init__(self):
        super().__init__(InterviewSessionScoreItem)

    def get_by_session(
        self,
        session: Session,
        interview_session_id: int,
    ) -> List[InterviewSessionScoreItem]:
        """
        获取面试场次的所有评分项（按排序）
        """
        stmt = (
            select(InterviewSessionScoreItem)
            .where(InterviewSessionScoreItem.session_id == interview_session_id)
            .where(InterviewSessionScoreItem.is_deleted == 0)
            .order_by(InterviewSessionScoreItem.order_no)
        )
        return list(session.execute(stmt).scalars().all())

    def add_score_item(
        self,
        session: Session,
        interview_session_id: int,
        score_item_id: int,
        order_no: int,
    ) -> InterviewSessionScoreItem:
        """
        添加评分项到场次
        """
        # 检查是否已存在
        existing = session.execute(
            select(InterviewSessionScoreItem)
            .where(InterviewSessionScoreItem.session_id == interview_session_id)
            .where(InterviewSessionScoreItem.score_item_id == score_item_id)
            .where(InterviewSessionScoreItem.is_deleted == 0)
        ).scalar_one_or_none()

        if existing:
            # 更新排序
            existing.order_no = order_no
            session.commit()
            session.refresh(existing)
            return existing

        relation = InterviewSessionScoreItem(
            session_id=interview_session_id,
            score_item_id=score_item_id,
            order_no=order_no,
        )
        session.add(relation)
        session.commit()
        session.refresh(relation)
        return relation

    def remove_score_item(
        self,
        session: Session,
        interview_session_id: int,
        score_item_id: int,
    ):
        """
        从场次移除评分项
        """
        relation = session.execute(
            select(InterviewSessionScoreItem)
            .where(InterviewSessionScoreItem.session_id == interview_session_id)
            .where(InterviewSessionScoreItem.score_item_id == score_item_id)
            .where(InterviewSessionScoreItem.is_deleted == 0)
        ).scalar_one_or_none()

        if relation:
            self.soft_delete(session, relation)
            session.commit()

    def set_score_items(
        self,
        session: Session,
        interview_session_id: int,
        score_item_ids: List[int],
    ):
        """
        设置场次的评分项列表（先删除旧的，再添加新的）
        """
        # 删除现有关联
        existing_relations = session.execute(
            select(InterviewSessionScoreItem)
            .where(InterviewSessionScoreItem.session_id == interview_session_id)
            .where(InterviewSessionScoreItem.is_deleted == 0)
        ).scalars().all()

        for relation in existing_relations:
            self.soft_delete(session, relation)

        # 添加新关联
        for index, score_item_id in enumerate(score_item_ids):
            relation = InterviewSessionScoreItem(
                session_id=interview_session_id,
                score_item_id=score_item_id,
                order_no=index + 1,
            )
            session.add(relation)

        session.commit()
