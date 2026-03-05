from typing import Optional, List
from sqlmodel import Session, select

from app.models.score_item import ScoreItem
from app.repositories.base import BaseRepository


class ScoreItemRepository(BaseRepository[ScoreItem]):
    """
    评分项仓储
    """

    def __init__(self):
        super().__init__(ScoreItem)

    def get_by_template(
        self,
        session: Session,
        template_id: int,
    ) -> List[ScoreItem]:
        """
        获取模板的所有评分项

        Args:
            session: 数据库会话
            template_id: 模板ID

        Returns:
            评分项列表（按order_no排序）
        """
        stmt = (
            select(ScoreItem)
            .where(ScoreItem.template_id == template_id)
            .where(ScoreItem.is_deleted == 0)
            .order_by(ScoreItem.order_no)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> List[ScoreItem]:
        """
        获取场次的评分项（自定义评分项）

        Args:
            session: 数据库会话
            session_id: 面试场次ID

        Returns:
            评分项列表（按order_no排序）
        """
        stmt = (
            select(ScoreItem)
            .where(ScoreItem.session_id == session_id)
            .where(ScoreItem.is_deleted == 0)
            .order_by(ScoreItem.order_no)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_template_or_session(
        self,
        session: Session,
        template_id: Optional[int] = None,
        session_id: Optional[int] = None,
    ) -> List[ScoreItem]:
        """
        获取评分项（从模板或场次）

        Args:
            session: 数据库会话
            template_id: 模板ID（优先）
            session_id: 场次ID（当template_id为空时使用）

        Returns:
            评分项列表（按order_no排序）
        """
        if template_id:
            return self.get_by_template(session, template_id)
        elif session_id:
            return self.get_by_session(session, session_id)
        return []

    def delete_by_session(
        self,
        session: Session,
        session_id: int,
    ) -> None:
        """
        删除场次的所有评分项（软删除）

        Args:
            session: 数据库会话
            session_id: 面试场次ID
        """
        stmt = (
            select(ScoreItem)
            .where(ScoreItem.session_id == session_id)
            .where(ScoreItem.is_deleted == 0)
        )
        items = session.execute(stmt).scalars().all()
        for item in items:
            self.soft_delete(session, item)
