from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.user_account import UserAccountRepository


class AuthenticationError(Exception):
    """用于 token 校验过程中的内部异常"""
    pass


bearer_scheme = HTTPBearer(auto_error=False)
user_repo = UserAccountRepository()



def get_current_user_by_token(
    token: str,
    session: Session,
) -> UserAccount:
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise AuthenticationError(str(e))

    user_id = payload.get("user_id")
    token_version = payload.get("token_version")

    if user_id is None or token_version is None:
        raise AuthenticationError("Invalid token payload")

    user = user_repo.get_by_id(session, user_id)
    if not user:
        raise AuthenticationError("User not found")

    if user.is_deleted == 1:
        raise AuthenticationError("User deleted")

    if user.status != 1:
        raise AuthenticationError("User is disabled")

    if user.token_version != token_version:
        raise AuthenticationError("Token has been revoked")

    return user



def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> UserAccount:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    try:
        return get_current_user_by_token(token, session)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


def get_interviewer_club_id(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> int:
    """
    获取面试官所属的社团ID

    通过 UserRole 表查询用户是否为某社团的面试官（INTERVIEWER角色）
    返回第一个关联的社团ID
    如果用户不是任何社团的面试官，则抛出 403 错误
    """
    # 获取面试官角色
    stmt = (
        select(Role)
        .where(Role.code == "INTERVIEWER")
        .where(Role.is_deleted == 0)
    )
    interviewer_role = session.execute(stmt).scalar_one_or_none()

    if not interviewer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    # 查询用户的面试官角色关联
    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.role_id == interviewer_role.id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = session.execute(stmt).scalars().all()

    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是任何社团的面试官",
        )

    # 优先返回带 club_id 的面试官角色
    # 兼容历史数据中存在 club_id 为空的“通用面试官”记录
    valid_user_role = next(
        (user_role for user_role in user_roles if user_role.club_id is not None),
        None,
    )

    if not valid_user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您尚未加入任何社团，请先接受社团邀请",
        )

    return valid_user_role.club_id
