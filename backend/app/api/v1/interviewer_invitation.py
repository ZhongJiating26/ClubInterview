from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.storage import get_storage_service
from app.db.session import get_session
from app.models.club import Club
from app.models.interviewer_invitation import InterviewerInvitation
from app.models.role import Role
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.repositories.user_role import UserRoleRepository
from app.schemas.admin_compat import (
    InterviewerInvitationResponse,
    RejectInvitationRequest,
)


router = APIRouter(prefix="/interviewer", tags=["Interviewer Invitations"])
user_role_repo = UserRoleRepository()


def _success(data=None, message: str = "success"):
    return {
        "code": 200,
        "data": data if data is not None else {"detail": message},
        "message": message,
    }


def _mark_expired_if_needed(session: Session, invitation: InterviewerInvitation, now: datetime) -> None:
    if invitation.status == "PENDING" and invitation.expired_at and invitation.expired_at <= now:
        invitation.status = "EXPIRED"
        invitation.touch()
        session.add(invitation)


def _build_invitation_response(
    session: Session,
    invitation: InterviewerInvitation,
    storage,
) -> InterviewerInvitationResponse:
    club = session.execute(
        select(Club)
        .where(Club.id == invitation.club_id)
        .where(Club.is_deleted == 0)
    ).scalar_one_or_none()
    inviter = None
    if invitation.inviter_id:
        inviter = session.execute(
            select(UserAccount)
            .where(UserAccount.id == invitation.inviter_id)
            .where(UserAccount.is_deleted == 0)
        ).scalar_one_or_none()

    return InterviewerInvitationResponse(
        id=invitation.id,
        club_id=invitation.club_id,
        club_name=club.name if club else "",
        club_logo_url=storage.get_object_url(club.logo_url) if club and club.logo_url else None,
        user_id=invitation.user_id,
        inviter_name=inviter.name if inviter else None,
        status=invitation.status,
        invite_code=invitation.invite_code,
        created_at=invitation.created_at.isoformat(),
    )


def _get_owned_invitation(session: Session, invitation_id: int, user_id: int) -> InterviewerInvitation:
    invitation = session.execute(
        select(InterviewerInvitation)
        .where(InterviewerInvitation.id == invitation_id)
        .where(InterviewerInvitation.user_id == user_id)
        .where(InterviewerInvitation.is_deleted == 0)
    ).scalar_one_or_none()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请不存在",
        )
    return invitation


@router.get("/invitations", response_model=list[InterviewerInvitationResponse])
def get_my_invitations(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    now = datetime.utcnow()
    stmt = (
        select(InterviewerInvitation)
        .where(InterviewerInvitation.user_id == current_user.id)
        .where(InterviewerInvitation.is_deleted == 0)
        .order_by(InterviewerInvitation.created_at.desc())
    )
    invitations = session.execute(stmt).scalars().all()

    has_updates = False
    for invitation in invitations:
        old_status = invitation.status
        _mark_expired_if_needed(session, invitation, now)
        if invitation.status != old_status:
            has_updates = True

    if has_updates:
        session.commit()
        for invitation in invitations:
            session.refresh(invitation)

    storage = get_storage_service()
    return [
        _build_invitation_response(session, invitation, storage)
        for invitation in invitations
    ]


@router.post("/invitations/{invitation_id}/accept")
def accept_invitation(
    invitation_id: int,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    invitation = _get_owned_invitation(session, invitation_id, current_user.id)
    now = datetime.utcnow()
    _mark_expired_if_needed(session, invitation, now)

    if invitation.status == "EXPIRED":
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请已过期",
        )
    if invitation.status == "REJECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请已被拒绝，无法接受",
        )
    if invitation.status == "ACCEPTED":
        return _success({"detail": "您已接受该邀请"}, "接受成功")
    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请状态无效",
        )

    interviewer_role = session.execute(
        select(Role)
        .where(Role.code == "INTERVIEWER")
        .where(Role.is_deleted == 0)
    ).scalar_one_or_none()
    if not interviewer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    user_role_repo.assign_role(
        session,
        user_id=current_user.id,
        role_id=interviewer_role.id,
        club_id=invitation.club_id,
    )

    invitation.status = "ACCEPTED"
    invitation.touch()
    session.add(invitation)
    session.commit()

    return _success({"detail": "已接受邀请"}, "接受成功")


@router.post("/invitations/{invitation_id}/reject")
def reject_invitation(
    invitation_id: int,
    data: RejectInvitationRequest | None = None,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    invitation = _get_owned_invitation(session, invitation_id, current_user.id)
    now = datetime.utcnow()
    _mark_expired_if_needed(session, invitation, now)

    if invitation.status == "EXPIRED":
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请已过期",
        )
    if invitation.status == "ACCEPTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请已被接受，无法拒绝",
        )
    if invitation.status == "REJECTED":
        return _success({"detail": "您已拒绝该邀请"}, "拒绝成功")
    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请状态无效",
        )

    invitation.status = "REJECTED"
    invitation.touch()
    session.add(invitation)
    session.commit()

    return _success(
        {"detail": "已拒绝邀请", "reason": data.reason if data else None},
        "拒绝成功",
    )
