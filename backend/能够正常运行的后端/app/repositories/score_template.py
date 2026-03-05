from typing import Optional, List
from sqlmodel import Session, select

from app.models.score_template import ScoreTemplate
from app.models.score_item import ScoreItem
from app.repositories.base import BaseRepository


class ScoreTemplateRepository(BaseRepository[ScoreTemplate]):
    """
    评分模板仓储
    """

    def __init__(self):
        super().__init__(ScoreTemplate)

    def get_by_club(
        self,
        session: Session,
        club_id: int,
        status: Optional[str] = None,
    ) -> List[ScoreTemplate]:
        """
        获取社团的评分模板列表

        Args:
            session: 数据库会话
            club_id: 社团ID
            status: 状态筛选（ACTIVE/INACTIVE）

        Returns:
            评分模板列表
        """
        stmt = (
            select(ScoreTemplate)
            .where(ScoreTemplate.club_id == club_id)
            .where(ScoreTemplate.is_deleted == 0)
        )

        if status:
            stmt = stmt.where(ScoreTemplate.status == status)

        stmt = stmt.order_by(ScoreTemplate.created_at.desc())
        return list(session.execute(stmt).scalars().all())

    def get_default_template(
        self,
        session: Session,
        club_id: int,
    ) -> Optional[ScoreTemplate]:
        """
        获取社团的默认模板

        Args:
            session: 数据库会话
            club_id: 社团ID

        Returns:
            默认评分模板，如果不存在则返回None
        """
        # 注意：ScoreTemplate模型中没有is_default字段
        # 这里返回最近创建的ACTIVE模板作为默认模板
        stmt = (
            select(ScoreTemplate)
            .where(ScoreTemplate.club_id == club_id)
            .where(ScoreTemplate.status == "ACTIVE")
            .where(ScoreTemplate.is_deleted == 0)
            .order_by(ScoreTemplate.created_at.asc())
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_with_items(
        self,
        session: Session,
        template_id: int,
    ) -> Optional[ScoreTemplate]:
        """
        获取模板及其评分项

        Args:
            session: 数据库会话
            template_id: 模板ID

        Returns:
            评分模板对象（包含items属性）
        """
        template = self.get(session, template_id)
        if template:
            # 获取关联的评分项
            stmt = (
                select(ScoreItem)
                .where(ScoreItem.template_id == template_id)
                .where(ScoreItem.is_deleted == 0)
                .order_by(ScoreItem.order_no)
            )
            template.items = list(session.execute(stmt).scalars().all())
        return template
