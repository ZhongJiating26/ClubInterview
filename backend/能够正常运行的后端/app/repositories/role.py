from typing import List, Optional
from sqlmodel import Session, select, join

from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """
    角色仓储
    """

    def __init__(self):
        super().__init__(Role)

    def get_by_code(self, session: Session, code: str) -> Optional[Role]:
        """根据角色编码查询"""
        stmt = (
            select(Role)
            .where(Role.code == code)
            .where(Role.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_user_roles(self, session: Session, user_id: int) -> List[Role]:
        """
        获取用户的角色列表
        """
        stmt = (
            select(Role)
            .select_from(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(UserRole.is_deleted == 0)
            .where(Role.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())

    def get_user_role_codes(self, session: Session, user_id: int) -> List[str]:
        """
        获取用户的角色编码列表（如 ['STUDENT', 'INTERVIEWER']）
        """
        roles = self.get_user_roles(session, user_id)
        return [role.code for role in roles]
