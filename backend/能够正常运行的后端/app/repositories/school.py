from typing import List, Optional
from sqlmodel import Session, select, or_

from app.models.school import School
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    """
    学校仓储
    """

    def __init__(self):
        super().__init__(School)

    def get_by_code(self, session: Session, code: str) -> Optional[School]:
        """
        根据学校标识码查询学校
        """
        stmt = (
            select(School)
            .where(School.code == code)
            .where(School.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def search_by_name(
        self,
        session: Session,
        keyword: str,
        limit: int = 20,
    ) -> List[School]:
        """
        根据关键词搜索学校（模糊匹配）
        """
        if not keyword or len(keyword.strip()) == 0:
            return []

        stmt = (
            select(School)
            .where(School.name.contains(keyword.strip()))
            .where(School.is_deleted == 0)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())
