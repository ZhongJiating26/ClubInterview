from typing import Optional
from sqlmodel import Session, select

from app.models.club_position import ClubPosition
from app.repositories.base import BaseRepository


class ClubPositionRepository(BaseRepository[ClubPosition]):
    """
    岗位仓储
    """

    def __init__(self):
        super().__init__(ClubPosition)

    def get_by_club(
        self,
        session: Session,
        club_id: int,
        department_id: Optional[int] = None,
    ) -> list[ClubPosition]:
        """
        获取社团的岗位列表
        """
        stmt = (
            select(ClubPosition)
            .where(ClubPosition.club_id == club_id)
            .where(ClubPosition.is_deleted == 0)
        )
        if department_id:
            stmt = stmt.where(ClubPosition.department_id == department_id)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(
        self,
        session: Session,
        club_id: int,
        name: str,
    ) -> Optional[ClubPosition]:
        """
        检查社团内是否存在同名岗位
        """
        stmt = (
            select(ClubPosition)
            .where(ClubPosition.club_id == club_id)
            .where(ClubPosition.name == name)
            .where(ClubPosition.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()
