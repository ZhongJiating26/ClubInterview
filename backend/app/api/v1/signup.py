from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, and_

from app.db.session import get_session
from app.models.signup_session import SignupSession
from app.models.signup_item import SignupItem
from app.models.signup_attachment import SignupAttachment
from app.models.club_position import ClubPosition
from app.models.recruitment_session import RecruitmentSession
from app.models.user_account import UserAccount
from app.repositories.recruitment_session import RecruitmentSessionRepository
from app.repositories.signup_session import (
    SignupSessionRepository, SignupItemRepository, SignupAttachmentRepository,
)
from app.repositories.user_account import UserAccountRepository
from app.schemas.signup_session import (
    SignupSubmitRequest, SignupSessionResponse, SignupSessionListResponse,
    SignupAuditRequest, SignupAuditResponse, SignupItemResponse, SignupAttachmentResponse,
    SignupApplicationResponse, SignupApplicationListResponse,
)
from app.api.deps import get_current_user, get_interviewer_club_id


router = APIRouter(tags=["报名管理"])
session_repo = RecruitmentSessionRepository()
signup_repo = SignupSessionRepository()
item_repo = SignupItemRepository()
attachment_repo = SignupAttachmentRepository()
user_account_repo = UserAccountRepository()


def _load_signup(session: Session, signup: SignupSession) -> SignupSessionResponse:
    """加载报名详情（包含岗位和附件）"""
    items = item_repo.get_by_session(session, signup.id)
    attachments = attachment_repo.get_by_session(session, signup.id)

    return SignupSessionResponse(
        id=signup.id,
        user_id=signup.user_id,
        recruitment_session_id=signup.recruitment_session_id,
        self_intro=signup.self_intro,
        status=signup.status,
        audit_user_id=signup.audit_user_id,
        audit_time=signup.audit_time,
        audit_reason=signup.audit_reason,
        created_at=signup.created_at,
        updated_at=signup.updated_at,
        items=[SignupItemResponse.model_validate(i) for i in items],
        attachments=[SignupAttachmentResponse.model_validate(a) for a in attachments],
    )


def _load_signup_with_user(session: Session, signup: SignupSession) -> SignupApplicationResponse:
    """加载报名详情（包含用户信息，用于审核）"""
    # 获取用户信息
    user = user_account_repo.get(session, signup.user_id)

    # 获取招新场次名称
    from app.models.recruitment_session import RecruitmentSession
    from app.repositories.recruitment_session import RecruitmentSessionRepository
    recruitment_repo = RecruitmentSessionRepository()
    recruitment = recruitment_repo.get(session, signup.recruitment_session_id)
    session_name = recruitment.name if recruitment else None

    items = item_repo.get_by_session(session, signup.id)
    attachments = attachment_repo.get_by_session(session, signup.id)

    return SignupApplicationResponse(
        id=signup.id,
        user_id=signup.user_id,
        user_name=user.name if user else None,
        user_phone=user.phone if user else "",
        user_email=user.email if user else None,
        recruitment_session_id=signup.recruitment_session_id,
        session_name=session_name,
        self_intro=signup.self_intro,
        status=signup.status,
        audit_user_id=signup.audit_user_id,
        audit_time=signup.audit_time,
        audit_reason=signup.audit_reason,
        created_at=signup.created_at,
        updated_at=signup.updated_at,
        items=[SignupItemResponse.model_validate(i) for i in items],
        attachments=[SignupAttachmentResponse.model_validate(a) for a in attachments],
    )


# ==================== 学生端接口 ====================

@router.post("/signup", response_model=SignupSessionResponse, status_code=status.HTTP_201_CREATED)
def submit_signup(
    data: SignupSubmitRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    学生提交报名
    """
    # 检查招新场次是否存在且在报名时间内
    if not session_repo.is_registration_open(session, data.recruitment_session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="招新场次不在报名时间内或未发布",
        )

    # 检查是否已报名（未删除的）
    existing = signup_repo.get_by_user_and_session(
        session, current_user.id, data.recruitment_session_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已报名该招新场次",
        )

    # 验证岗位是否存在且属于该招新场次
    for p in data.positions:
        position = session.get(ClubPosition, p.position_id)
        if not position or position.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"岗位 {p.position_id} 不存在",
            )

    # 创建报名主表
    signup = SignupSession(
        user_id=current_user.id,
        recruitment_session_id=data.recruitment_session_id,
        self_intro=data.self_intro,
        status="PENDING",
    )
    session.add(signup)
    session.flush()

    # 创建报名子表
    for p in data.positions:
        item = SignupItem(
            signup_session_id=signup.id,
            department_id=p.department_id,
            position_id=p.position_id,
        )
        session.add(item)

    session.commit()
    session.refresh(signup)

    return _load_signup(session, signup)


# ==================== 面试官端接口 ====================

@router.get("/interviewer/signup/applications", response_model=SignupApplicationListResponse)
def list_interviewer_signup_applications(
    recruitment_session_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    club_id: int = Depends(get_interviewer_club_id),
    session: Session = Depends(get_session),
):
    """
    查询报名申请列表（面试官）

    根据当前面试官的 club_id 返回该社团的报名数据
    支持按招新场次 ID 和状态筛选，支持分页
    """
    # 构建查询条件
    conditions = [
        SignupSession.is_deleted == 0,
    ]

    # 如果指定了 recruitment_session_id，直接使用
    if recruitment_session_id:
        # 验证该场次是否属于当前面试官的社团
        rs = session.get(RecruitmentSession, recruitment_session_id)
        if not rs or rs.is_deleted or rs.club_id != club_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="招新场次不存在或不属于您的社团",
            )
        conditions.append(SignupSession.recruitment_session_id == recruitment_session_id)
    else:
        # 如果没有指定场次，返回该社团所有场次的报名
        conditions.append(RecruitmentSession.club_id == club_id)

    # 如果指定了状态筛选
    if status:
        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值，可选值：{', '.join(valid_statuses)}",
            )
        conditions.append(SignupSession.status == status)

    # 查询报名记录
    stmt = (
        select(SignupSession)
        .join(RecruitmentSession, SignupSession.recruitment_session_id == RecruitmentSession.id)
        .where(and_(*conditions))
        .order_by(SignupSession.created_at.desc())
    )
    signups = session.execute(stmt).scalars().all()

    total = len(signups)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = signups[start:end]

    items = [_load_signup_with_user(session, s) for s in paginated]

    return SignupApplicationListResponse(items=items, total=total)


# ==================== 管理端接口 ====================

@router.get("/admin/signup/applications", response_model=SignupApplicationListResponse)
def list_signup_applications(
    recruitment_session_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    获取报名审核列表（社团管理员）

    返回包含用户信息的报名列表，支持分页
    """
    # 验证招新场次是否存在
    recruitment = session.get(RecruitmentSession, recruitment_session_id)
    if not recruitment or recruitment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # TODO: 验证当前用户是否为该社团的管理员

    signups = signup_repo.get_by_session(session, recruitment_session_id, status)
    total = len(signups)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = signups[start:end]

    items = [_load_signup_with_user(session, s) for s in paginated]

    return SignupApplicationListResponse(items=items, total=total)


@router.get("/admin/signup/applications/{signup_id}", response_model=SignupApplicationResponse)
def get_signup_application(
    signup_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    获取报名详情（社团管理员/面试官）

    返回包含用户信息的完整报名详情
    """
    signup = signup_repo.get(session, signup_id)
    if not signup or signup.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报名记录不存在",
        )

    return _load_signup_with_user(session, signup)


@router.post("/admin/signup/applications/{signup_id}/audit", response_model=SignupAuditResponse)
def audit_signup(
    signup_id: int,
    data: SignupAuditRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    审核报名（社团管理员）
    """
    signup = signup_repo.get(session, signup_id)
    if not signup or signup.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报名记录不存在",
        )
    if signup.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="报名已审核",
        )

    # 更新报名状态
    signup.status = data.status
    signup.audit_user_id = current_user.id
    signup.audit_time = datetime.now()
    if data.status == "REJECTED":
        signup.audit_reason = data.reason

    signup.touch()
    session.commit()
    session.refresh(signup)

    # TODO: 触发通知模块发送审核结果通知

    return SignupAuditResponse(
        detail="审核完成",
        signup_id=signup.id,
        new_status=signup.status,
    )


