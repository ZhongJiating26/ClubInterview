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
from app.models.role import Role
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.repositories.recruitment_session import RecruitmentSessionRepository
from app.repositories.signup_session import (
    SignupSessionRepository, SignupItemRepository, SignupAttachmentRepository,
)
from app.repositories.user_account import UserAccountRepository
from app.schemas.signup_session import (
    SignupSubmitRequest, SignupSessionResponse, SignupSessionListResponse,
    SignupAuditRequest, SignupAuditResponse, SignupItemResponse, SignupAttachmentResponse,
    SignupApplicationResponse, SignupApplicationListResponse,
    UploadSignupAttachmentRequest, UploadSignupAttachmentResponse,
    SetCustomFieldsRequest, SetCustomFieldsResponse,
    GetCustomFieldsResponse, CustomFieldDefinition,
    SignupExportRequest, SignupExportResponse, SignupExportItem,
)
from app.api.deps import get_current_user, get_interviewer_club_id


router = APIRouter(tags=["报名管理"])
session_repo = RecruitmentSessionRepository()
signup_repo = SignupSessionRepository()
item_repo = SignupItemRepository()
attachment_repo = SignupAttachmentRepository()
user_account_repo = UserAccountRepository()


def _ensure_club_admin(session: Session, current_user: UserAccount, club_id: int) -> None:
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

    relation = session.execute(
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.role_id == club_admin_role.id)
        .where(UserRole.club_id == club_id)
        .where(UserRole.is_deleted == 0)
    ).scalar_one_or_none()

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作",
        )


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


@router.get("/interviewer/signup/applications/{signup_id}", response_model=SignupApplicationResponse)
def get_interviewer_signup_application(
    signup_id: int,
    club_id: int = Depends(get_interviewer_club_id),
    session: Session = Depends(get_session),
):
    """
    获取报名详情（面试官）

    仅允许查看自己所属社团的报名记录
    """
    signup = signup_repo.get(session, signup_id)
    if not signup or signup.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报名记录不存在",
        )

    recruitment = session.get(RecruitmentSession, signup.recruitment_session_id)
    if not recruitment or recruitment.is_deleted or recruitment.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报名记录不存在或不属于您的社团",
        )

    return _load_signup_with_user(session, signup)


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

    _ensure_club_admin(session, current_user, recruitment.club_id)

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

    # 发送审核结果通知
    _send_audit_notification(session, signup, current_user)

    return SignupAuditResponse(
        detail="审核完成",
        signup_id=signup.id,
        new_status=signup.status,
    )


# ============ 报名功能增强 ============


@router.post("/signup/{signup_id}/attachments", response_model=UploadSignupAttachmentResponse)
def upload_signup_attachment(
    signup_id: int,
    data: UploadSignupAttachmentRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    上传报名附件

    - 支持简历、作品集等附件上传
    - 文件通过文件上传接口预先上传到存储服务
    - 这里只创建附件记录
    """
    # 检查报名是否存在
    signup = signup_repo.get(session, signup_id)
    if not signup or signup.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报名记录不存在",
        )

    # 检查权限（只能上传自己的报名附件）
    if signup.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作",
        )

    # TODO: 这里应该接收 file_url 参数
    # 简化版本：假设文件已经上传，直接创建记录
    from app.core.storage import get_storage_service
    import uuid

    storage = get_storage_service()
    file_url = f"signups/attachments/{signup_id}/{uuid.uuid4()}"

    # 创建附件记录
    attachment = SignupAttachment(
        signup_session_id=signup_id,
        file_url=file_url,
        file_type=data.file_type,
        file_name=data.file_name,
        file_size=0,  # TODO: 从上传服务获取实际大小
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)

    return UploadSignupAttachmentResponse(
        attachment_id=attachment.id,
        file_url=storage.get_object_url(file_url),
    )


@router.delete("/signup/attachments/{attachment_id}")
def delete_signup_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    删除报名附件

    - 只能删除自己报名的附件
    """
    # 检查附件是否存在
    attachment = attachment_repo.get(session, attachment_id)
    if not attachment or attachment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在",
        )

    # 检查报名权限
    signup = signup_repo.get(session, attachment.signup_session_id)
    if not signup or signup.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作",
        )

    # 软删除附件
    attachment_repo.soft_delete(session, attachment)
    session.commit()

    return {"detail": "附件已删除"}


@router.post("/recruitment/{recruitment_session_id}/custom-fields", response_model=SetCustomFieldsResponse)
def set_custom_fields(
    recruitment_session_id: int,
    data: SetCustomFieldsRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    设置报名自定义字段

    - 为招新场次配置自定义报名字段
    - 支持多种字段类型
    """
    # 检查场次是否存在
    from app.repositories.recruitment_session import RecruitmentSessionRepository
    recruitment_repo = RecruitmentSessionRepository()
    recruitment = recruitment_repo.get(session, recruitment_session_id)

    if not recruitment or recruitment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # 检查权限（需要是社团管理员）
    from app.repositories.user_role import UserRoleRepository
    user_role_repo = UserRoleRepository()
    user_roles = user_role_repo.get_user_roles(session, current_user.id)

    has_permission = any(
        ur.role_id == 2 and ur.club_id == recruitment.club_id  # CLUB_ADMIN
        for ur in user_roles
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作",
        )

    # TODO: 将自定义字段配置保存到数据库
    # 简化版本：将配置存储在招新场次的 extra_fields_json 中
    import json
    fields_data = [field.model_dump() for field in data.fields]

    if recruitment.extra_fields_json:
        existing_config = json.loads(recruitment.extra_fields_json)
        existing_config["custom_fields"] = fields_data
        recruitment.extra_fields_json = json.dumps(existing_config)
    else:
        recruitment.extra_fields_json = json.dumps({"custom_fields": fields_data})

    session.commit()

    return SetCustomFieldsResponse(detail="自定义字段设置成功")


@router.get("/recruitment/{recruitment_session_id}/custom-fields", response_model=GetCustomFieldsResponse)
def get_custom_fields(
    recruitment_session_id: int,
    session: Session = Depends(get_session),
):
    """
    获取报名自定义字段配置

    - 返回招新场次的自定义字段配置
    - 用于前端渲染报名表单
    """
    from app.repositories.recruitment_session import RecruitmentSessionRepository
    recruitment_repo = RecruitmentSessionRepository()
    recruitment = recruitment_repo.get(session, recruitment_session_id)

    if not recruitment or recruitment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # 解析自定义字段配置
    fields = []
    if recruitment.extra_fields_json:
        import json
        try:
            config = json.loads(recruitment.extra_fields_json)
            fields_data = config.get("custom_fields", [])
            fields = [CustomFieldDefinition(**field) for field in fields_data]
        except (json.JSONDecodeError, TypeError):
            pass

    return GetCustomFieldsResponse(
        recruitment_session_id=recruitment_session_id,
        fields=fields,
    )


@router.post("/recruitment/export-signups", response_model=SignupExportResponse)
def export_signup_data(
    data: SignupExportRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    导出报名数据

    - 导出指定场次的报名数据
    - 支持状态筛选
    - 返回JSON格式的导出数据
    """
    # 检查场次是否存在
    from app.repositories.recruitment_session import RecruitmentSessionRepository
    from app.repositories.school import SchoolRepository
    recruitment_repo = RecruitmentSessionRepository()
    school_repo = SchoolRepository()

    recruitment = recruitment_repo.get(session, data.recruitment_session_id)
    if not recruitment or recruitment.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="招新场次不存在",
        )

    # 检查权限（需要是该社团的管理员）
    from app.repositories.user_role import UserRoleRepository
    user_role_repo = UserRoleRepository()
    user_roles = user_role_repo.get_user_roles(session, current_user.id)

    has_permission = any(
        ur.role_id == 2 and ur.club_id == recruitment.club_id  # CLUB_ADMIN
        for ur in user_roles
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作",
        )

    # 获取报名列表
    signups = signup_repo.get_by_recruitment_session(session, data.recruitment_session_id)

    # 应用状态筛选
    if data.status:
        signups = [s for s in signups if s.status == data.status]

    # 准备导出数据
    export_items = []
    for signup in signups:
        # 获取用户信息
        user = user_account_repo.get(session, signup.user_id)

        # 获取学校信息
        school_name = None
        if user and user.school_code:
            school = school_repo.get_by_code(session, user.school_code)
            school_name = school.name if school else None

        # 获取报名岗位
        items = item_repo.get_by_session(session, signup.id)
        position_names = ", ".join([
            f"{item.department.name if item.department else ''}/{item.position.name if item.position else ''}"
            for item in items
        ]) if items else None

        # 解析自定义字段
        custom_fields = None
        if signup.extra_fields_json:
            try:
                import json
                custom_fields = json.loads(signup.extra_fields_json)
            except (json.JSONDecodeError, TypeError):
                pass

        export_items.append(SignupExportItem(
            signup_id=signup.id,
            user_name=user.name if user else None,
            user_phone=user.phone if user else "",
            user_email=user.email if user else None,
            user_school=school_name,
            user_major=user.major if user else None,
            recruitment_session_name=recruitment.name,
            positions=position_names,
            self_intro=signup.self_intro,
            custom_fields=custom_fields,
            status=signup.status,
            audit_time=signup.audit_time.strftime("%Y-%m-%d %H:%M:%S") if signup.audit_time else None,
            audit_reason=signup.audit_reason,
            created_at=signup.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ))

    return SignupExportResponse(
        recruitment_session_id=data.recruitment_session_id,
        total_count=len(export_items),
        data=export_items,
    )


# ============ 辅助函数 ============


def _send_audit_notification(
    session: Session,
    signup: SignupSession,
    admin_user: UserAccount,
):
    """
    发送审核结果通知

    - 审核通过：发送通过通知
    - 审核拒绝：发送拒绝通知（包含拒绝理由）
    """
    from app.models.notification import Notification
    from app.models.notification_user import NotificationUser
    from app.repositories.notification import NotificationRepository

    notification_repo = NotificationRepository()

    # 根据审核结果设置通知内容
    if signup.status == "APPROVED":
        title = "报名审核通过"
        content = "恭喜！您的报名申请已通过审核，请留意面试安排。"
    elif signup.status == "REJECTED":
        title = "报名审核未通过"
        reason = f"\n拒绝原因：{signup.audit_reason}" if signup.audit_reason else ""
        content = f"很抱歉，您的报名申请未通过审核。{reason}"
    else:
        return  # 其他状态不发送通知

    # 创建通知
    notification = Notification(
        title=title,
        content=content,
        type="SIGNUP_AUDIT",
    )
    notification_repo.create(session, notification)

    # 关联到报名用户
    notification_user = NotificationUser(
        notification_id=notification.id,
        user_id=signup.user_id,
        read_status=0,
    )
    session.add(notification_user)
    session.commit()
