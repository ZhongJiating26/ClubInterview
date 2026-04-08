from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.storage import get_storage_service
from app.db.session import get_session
from app.models.club import Club
from app.models.interviewer_invitation import InterviewerInvitation
from app.models.notification import Notification
from app.models.notification_user import NotificationUser
from app.models.role import Role
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.schemas.admin_compat import (
    AdminUserSearchItem,
    AdminUserSearchResponse,
    InterviewerInvitationResponse,
    InviteInterviewerRequest,
)


router = APIRouter(prefix="/admin", tags=["Admin Compatibility"])


def _success(data, message: str = "success"):
    return {
        "code": 200,
        "data": data,
        "message": message,
    }


def _ensure_club_admin(session: Session, current_user: UserAccount, club_id: int | None = None) -> None:
    club_admin_role = session.execute(
        select(Role)
        .where(Role.code == "CLUB_ADMIN")
        .where(Role.is_deleted == 0)
    ).scalar_one_or_none()

    if not club_admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.role_id == club_admin_role.id)
        .where(UserRole.is_deleted == 0)
    )
    if club_id is not None:
        stmt = stmt.where(UserRole.club_id == club_id)

    relation = session.execute(stmt).scalar_one_or_none()
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限执行该操作",
        )


@router.get("/users/search")
def search_users(
    phone: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    管理端按手机号搜索用户
    """
    _ensure_club_admin(session, current_user)

    keyword = phone.strip()
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="手机号不能为空",
        )

    stmt = (
        select(UserAccount)
        .where(UserAccount.is_deleted == 0)
        .where(UserAccount.status == 1)
        .where(UserAccount.phone.contains(keyword))
        .order_by(UserAccount.id.desc())
    )
    users = session.execute(stmt).scalars().all()

    data = AdminUserSearchResponse(
        items=[
            AdminUserSearchItem(
                id=user.id,
                name=user.name,
                phone=user.phone,
            )
            for user in users
        ],
        total=len(users),
    )
    return _success(data.model_dump(), "查询成功")


@router.post("/clubs/{club_id}/invite-interviewer")
def invite_interviewer(
    club_id: int,
    data: InviteInterviewerRequest,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    邀请用户成为社团面试官
    """
    _ensure_club_admin(session, current_user, club_id)

    club = session.execute(
        select(Club)
        .where(Club.id == club_id)
        .where(Club.is_deleted == 0)
    ).scalar_one_or_none()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    target_user = session.execute(
        select(UserAccount)
        .where(UserAccount.id == data.user_id)
        .where(UserAccount.is_deleted == 0)
        .where(UserAccount.status == 1)
    ).scalar_one_or_none()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能邀请自己成为面试官",
        )

    interviewer_role = session.execute(
        select(Role)
        .where(Role.code == "INTERVIEWER")
        .where(Role.is_deleted == 0)
    ).scalar_one_or_none()
    club_admin_role = session.execute(
        select(Role)
        .where(Role.code == "CLUB_ADMIN")
        .where(Role.is_deleted == 0)
    ).scalar_one_or_none()
    if not interviewer_role or not club_admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    existing_member = session.execute(
        select(UserRole)
        .where(UserRole.user_id == target_user.id)
        .where(UserRole.club_id == club_id)
        .where(UserRole.is_deleted == 0)
        .where(UserRole.role_id.in_([interviewer_role.id, club_admin_role.id]))
    ).scalar_one_or_none()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已是本社团成员，无需重复邀请",
        )

    now = datetime.utcnow()
    existing_invitation = session.execute(
        select(InterviewerInvitation)
        .where(InterviewerInvitation.club_id == club_id)
        .where(InterviewerInvitation.user_id == target_user.id)
        .where(InterviewerInvitation.is_deleted == 0)
        .where(InterviewerInvitation.status == "PENDING")
        .order_by(InterviewerInvitation.created_at.desc())
    ).scalar_one_or_none()
    if existing_invitation and (
        existing_invitation.expired_at is None or existing_invitation.expired_at > now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已有待处理邀请，请勿重复发送",
        )

    invitation = InterviewerInvitation(
        club_id=club_id,
        user_id=target_user.id,
        invite_code=uuid4().hex[:12].upper(),
        status="PENDING",
        expired_at=now + timedelta(days=7),
        inviter_id=current_user.id,
    )
    session.add(invitation)
    session.flush()

    notification = Notification(
        type="INTERVIEWER_INVITATION",
        title=f"{club.name} 面试官邀请",
        content=f"您收到来自社团“{club.name}”的面试官邀请，请登录系统处理。",
        biz_id=invitation.id,
        sent_at=now,
        status="SENT",
    )
    session.add(notification)
    session.flush()

    session.add(NotificationUser(
        notification_id=notification.id,
        user_id=target_user.id,
        read_status="UNREAD",
    ))
    session.commit()
    session.refresh(invitation)

    storage = get_storage_service()
    response = InterviewerInvitationResponse(
        id=invitation.id,
        club_id=club.id,
        club_name=club.name,
        club_logo_url=storage.get_object_url(club.logo_url) if club.logo_url else None,
        user_id=target_user.id,
        inviter_name=current_user.name,
        status=invitation.status,
        invite_code=invitation.invite_code,
        created_at=invitation.created_at.isoformat(),
    )
    return _success(response.model_dump(), "邀请发送成功")
