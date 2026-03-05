from typing import Optional
from sqlmodel import Session, select

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """
    部门仓储
    """

    def __init__(self):
        super().__init__(Department)

    def get_by_club(
        self,
        session: Session,
        club_id: int,
    ) -> list[Department]:
        """
        获取社团的所有部门
        """
        stmt = (
            select(Department)
            .where(Department.club_id == club_id)
            .where(Department.is_deleted == 0)
            .order_by(Department.created_at.desc())
        )
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(
        self,
        session: Session,
        club_id: int,
        name: str,
    ) -> Optional[Department]:
        """
        检查社团内是否存在同名部门
        """
        stmt = (
            select(Department)
            .where(Department.club_id == club_id)
            .where(Department.name == name)
            .where(Department.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()
