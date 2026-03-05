from typing import Optional
from sqlmodel import Session, select

from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.base import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    """
    用户角色关联仓储
    """

    def __init__(self):
        super().__init__(UserRole)

    def assign_role(
        self,
        session: Session,
        user_id: int,
        role_id: int,
        club_id: Optional[int] = None,
    ) -> UserRole:
        """
        为用户分配角色
        """
        # 检查是否已存在该角色分配（未删除）
        stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
        )
        existing = session.execute(stmt).scalar_one_or_none()
        if existing:
            return existing  # 已存在直接返回

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            club_id=club_id,
        )
        return self.create(session, user_role)

    def revoke_role(
        self,
        session: Session,
        user_id: int,
        role_id: int,
        club_id: Optional[int] = None,
    ) -> bool:
        """
        撤销用户角色（软删除）
        """
        stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
        )
        user_role = session.execute(stmt).scalar_one_or_none()
        if user_role:
            self.soft_delete(session, user_role)
            return True
        return False

    def get_user_roles(
        self,
        session: Session,
        user_id: int,
    ) -> list[UserRole]:
        """
        获取用户的所有角色
        """
        stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.is_deleted == 0)
        )
        result = session.execute(stmt)
        return list(result.scalars().all())

    def get_by_user_role_club(
        self,
        session: Session,
        user_id: int,
        role_id: int,
        club_id: int,
    ) -> Optional[UserRole]:
        """
        检查用户是否已有某角色（用于特定社团）
        """
        stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()
