from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.club import Club
from app.models.interviewer_invitation import InterviewerInvitation
from app.models.notification import Notification
from app.models.notification_user import NotificationUser
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.user_account import UserAccount
from app.models.recruitment_session_position import RecruitmentSessionPosition
from app.repositories.club import ClubRepository
from app.repositories.role import RoleRepository
from app.repositories.user_account import UserAccountRepository
from app.repositories.user_role import UserRoleRepository
from app.repositories.department import DepartmentRepository
from app.repositories.club_position import ClubPositionRepository
from app.repositories.recruitment_session import (
    RecruitmentSessionRepository,
    RecruitmentSessionPositionRepository,
)
from app.schemas.club import (
    InitClubRequest, InitClubResponse,
    UpdateClubRequest, ClubResponse,
    ClubProfileCheckResponse,
    CheckClubRequest, CheckClubResponse,
    BindUserRequest, BindUserResponse,
    HomeClubItem, ClubDetailResponse,
    ClubListRequest, ClubListResponse, ClubListItem,
    AuditClubRequest, AuditClubResponse,
    ClubMemberItem, ClubMembersResponse,
    UpdateMemberRoleRequest, UpdateMemberRoleResponse,
    RemoveMemberRequest, RemoveMemberResponse,
    ClubStatsResponse,
)


router = APIRouter(prefix="/clubs", tags=["Club"])
club_repo = ClubRepository()
dept_repo = DepartmentRepository()
position_repo = ClubPositionRepository()
session_repo = RecruitmentSessionRepository()
session_position_repo = RecruitmentSessionPositionRepository()


def _ensure_club_admin(
    session: Session,
    current_user: UserAccount,
    club_id: int,
) -> None:
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
            detail="您没有权限执行该操作",
        )


@router.post("/check", response_model=CheckClubResponse)
def check_club(
    data: CheckClubRequest,
    session: Session = Depends(get_session),
):
    """
    检查社团是否存在

    返回社团是否已存在，帮助前端决定是否继续创建社团
    """
    existing = club_repo.get_by_name_and_school(
        session,
        name=data.club_name,
        school_code=data.school_code,
    )

    if existing:
        return CheckClubResponse(
            exists=True,
            club_id=existing.id,
            message="该学校已存在同名社团，请联系社长加入或使用其他名称",
        )

    return CheckClubResponse(
        exists=False,
        club_id=None,
        message="社团不存在，可以创建",
    )


@router.post("/init", response_model=InitClubResponse)
def init_club(
    data: InitClubRequest,
    session: Session = Depends(get_session),
):
    """
    初始化社团

    用户在信息初始化时填写社团名称：
    - 如果该学校已存在同名社团，返回错误
    - 如果不存在，创建新社团（待审核状态）
    """
    # 检查社团是否已存在
    existing = club_repo.get_by_name_and_school(
        session,
        name=data.club_name,
        school_code=data.school_code,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学校已存在同名社团",
        )

    # 创建新社团
    club = club_repo.create(
        session,
        Club(
            name=data.club_name,
            school_code=data.school_code,
            logo_url="dev/clubs/logos/club-logo-default.png",
            status="REVIEW",  # 新社团需要审核
        ),
    )

    return InitClubResponse(
        detail="社团创建成功，等待审核",
        club_id=club.id,
        is_new=True,
    )


@router.put("/{club_id}")
async def update_club(
    club_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    完善/修改社团信息

    支持两种请求格式：
    1. JSON: {"name": "...", "category": "...", "description": "...", "cert_file_url": "..."}
    2. multipart/form-data: name, category, description, logo (文件), cert_file (文件)

    需要社团管理员权限（后续实现）
    """
    from app.core.storage import get_storage_service

    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    if club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团已删除",
        )

    storage = get_storage_service()

    # 判断请求类型
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        # 处理 multipart/form-data（包含文件上传）
        form = await request.form()

        # 处理文本字段
        if form.get("name"):
            club.name = form.get("name")
        if form.get("category"):
            club.category = form.get("category")
        if form.get("description"):
            club.description = form.get("description")

        # 处理 logo 文件上传
        logo_file = form.get("logo")
        if logo_file and logo_file.filename:
            ext = logo_file.filename.split(".")[-1] if "." in logo_file.filename else "png"
            # 使用社团ID命名
            filename = f"club-logo-{club_id}.{ext}"
            content = await logo_file.read()
            key = storage.upload_bytes(
                data=content,
                filename=filename,
                paths=("clubs", "logos"),
            )
            club.logo_url = key

        # 处理认证证书文件上传
        cert_file = form.get("cert_file")
        if cert_file and cert_file.filename:
            ext = cert_file.filename.split(".")[-1] if "." in cert_file.filename else "pdf"
            # 使用社团ID命名
            filename = f"club-cert-{club_id}.{ext}"
            content = await cert_file.read()
            key = storage.upload_bytes(
                data=content,
                filename=filename,
                paths=("clubs", "certs"),
            )
            club.cert_file_url = key

    else:
        # 处理 JSON 请求
        body = await request.json()
        if body.get("name") is not None:
            club.name = body["name"]
        if body.get("category") is not None:
            club.category = body["category"]
        if body.get("description") is not None:
            club.description = body["description"]
        if body.get("logo_url") is not None:
            club.logo_url = body["logo_url"]
        if body.get("cert_file_url") is not None:
            club.cert_file_url = body["cert_file_url"]

    club.touch()
    session.commit()

    return {"detail": "更新成功"}


@router.get("/home-list", response_model=list[HomeClubItem])
def get_home_club_list(
    school_code: str,
    status: str = None,
    session: Session = Depends(get_session),
):
    """
    获取首页社团列表

    查询参数：
    - school_code: 学校编码（必填）
    - status: 社团状态筛选（可选，推荐使用 "ACTIVE" 表示活跃社团）

    返回该学校的社团列表，包含招新状态：
    - recruiting_status: "RECRUITING" 表示正在招新，"NO_RECRUITMENT" 表示暂无招新
    """
    # 兼容前端传的 APPROVED，映射到 ACTIVE
    if status == "APPROVED":
        status = "ACTIVE"

    clubs_data = club_repo.get_for_home(session, school_code, status)
    return clubs_data


@router.get("/{id}/detail", response_model=ClubDetailResponse)
def get_club_detail(
    id: int,
    session: Session = Depends(get_session),
):
    """
    获取社团完整详情

    返回社团的完整信息，包括：
    - 社团基本信息
    - 部门列表
    - 岗位列表
    - 招新场次列表
    """
    from app.core.storage import get_storage_service
    from app.repositories.school import SchoolRepository

    # 获取社团基本信息
    club = club_repo.get(session, id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    storage = get_storage_service()
    school_repo = SchoolRepository()

    # 获取学校名称
    school_name = None
    if club.school_code:
        school = school_repo.get_by_code(session, club.school_code)
        if school:
            school_name = school.name

    # 获取部门列表
    departments = dept_repo.get_by_club(session, id)
    departments_data = [
        {
            "id": d.id,
            "club_id": d.club_id,
            "name": d.name,
            "description": d.description,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat(),
        }
        for d in departments
    ]

    # 获取岗位列表
    positions = position_repo.get_by_club(session, id)
    positions_data = [
        {
            "id": p.id,
            "club_id": p.club_id,
            "department_id": p.department_id,
            "name": p.name,
            "description": p.description,
            "requirement": p.requirement,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in positions
    ]

    # 获取招新场次列表
    sessions = session_repo.get_by_club(session, id)
    sessions_data = []
    for s in sessions:
        # 获取场次关联的岗位（包含部门信息）
        from sqlmodel import select
        from app.models.department import Department
        from app.models.club_position import ClubPosition

        stmt = (
            select(RecruitmentSessionPosition, ClubPosition, Department)
            .join(ClubPosition, RecruitmentSessionPosition.position_id == ClubPosition.id)
            .outerjoin(Department, ClubPosition.department_id == Department.id)
            .where(RecruitmentSessionPosition.session_id == s.id)
            .where(RecruitmentSessionPosition.is_deleted == 0)
        )
        result = session.execute(stmt)
        positions_list = []
        for sp, p, d in result:
            positions_list.append({
                "id": sp.id,
                "session_id": sp.session_id,
                "position_id": sp.position_id,
                "department_id": p.department_id,
                "department_name": d.name if d else None,
                "position_name": sp.position_name,
                "position_description": sp.position_description,
                "position_requirement": sp.position_requirement,
                "recruit_quota": sp.recruit_quota,
            })

        sessions_data.append({
            "id": s.id,
            "club_id": s.club_id,
            "name": s.name,
            "description": s.description,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
            "max_candidates": s.max_candidates,
            "status": s.status,
            "created_by": s.created_by,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "positions": positions_list,
        })

    return ClubDetailResponse(
        id=club.id,
        school_name=school_name or "",
        name=club.name,
        logo_url=storage.get_object_url(club.logo_url) if club.logo_url else None,
        category=club.category,
        description=club.description,
        cert_file_url=storage.get_object_url(club.cert_file_url) if club.cert_file_url else None,
        status=club.status,
        created_at=club.created_at.isoformat() + "Z",
        departments=departments_data,
        positions=positions_data,
        recruitment_sessions=sessions_data,
    )


@router.get("/{club_id}", response_model=ClubResponse)
def get_club(
    club_id: int,
    session: Session = Depends(get_session),
):
    """
    获取社团详情
    """
    from app.core.storage import get_storage_service
    from app.repositories.school import SchoolRepository

    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    storage = get_storage_service()
    school_repo = SchoolRepository()

    # 获取学校名称
    school_name = None
    if club.school_code:
        school = school_repo.get_by_code(session, club.school_code)
        if school:
            school_name = school.name

    return ClubResponse(
        id=club.id,
        school_name=school_name or "",
        name=club.name,
        logo_url=storage.get_object_url(club.logo_url) if club.logo_url else None,
        category=club.category,
        description=club.description,
        cert_file_url=storage.get_object_url(club.cert_file_url) if club.cert_file_url else None,
        status=club.status,
        created_at=club.created_at.isoformat() + "Z",
    )


@router.get("/{club_id}/profile-check", response_model=ClubProfileCheckResponse)
def check_club_profile(
    club_id: int,
    session: Session = Depends(get_session),
):
    """
    检查社团资料是否填写完善

    检查字段：school_code、name、category、description、cert_file_url
    """
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查缺失字段
    missing_fields = []
    if not club.school_code:
        missing_fields.append("school_code")
    if not club.name:
        missing_fields.append("name")
    if not club.category:
        missing_fields.append("category")
    if not club.description:
        missing_fields.append("description")
    if not club.cert_file_url:
        missing_fields.append("cert_file_url")

    return ClubProfileCheckResponse(
        club_id=club.id,
        is_complete=len(missing_fields) == 0,
        missing_fields=missing_fields,
    )


@router.post("/{club_id}/bind-user", response_model=BindUserResponse)
def bind_user_to_club(
    club_id: int,
    data: BindUserRequest,
    session: Session = Depends(get_session),
):
    """
    将用户关联到社团（分配角色）

    用于社长创建社团后，关联自己为社团管理员
    或用于将其他用户添加到社团
    """
    user_repo = UserAccountRepository()
    role_repo = RoleRepository()
    user_role_repo = UserRoleRepository()

    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查用户是否存在
    user = user_repo.get(session, data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 检查角色是否存在
    role = role_repo.get(session, data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )

    # 检查用户是否已是该社团成员
    existing = user_role_repo.get_by_user_role_club(
        session,
        user_id=data.user_id,
        role_id=data.role_id,
        club_id=club_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已是该社团成员",
        )

    # 创建关联
    user_role = UserRole(
        user_id=data.user_id,
        role_id=data.role_id,
        club_id=club_id,
    )
    session.add(user_role)
    session.commit()

    return BindUserResponse(detail=f"用户已关联到社团，角色：{role.name}")


# ============ 社团管理增强功能 ============


@router.get("", response_model=ClubListResponse)
def get_club_list(
    school_code: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
):
    """
    获取社团列表（分页、搜索）

    - 支持按学校筛选
    - 支持按状态筛选（ACTIVE/INACTIVE/REVIEW）
    - 支持按分类筛选
    - 支持关键词搜索（社团名称）
    - 支持分页
    """
    result = club_repo.get_club_list(
        session,
        school_code=school_code,
        status=status,
        category=category,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    return ClubListResponse(
        items=[ClubListItem(**item) for item in result["items"]],
        total=result["total"],
        page=page,
        page_size=page_size,
    )


@router.post("/{club_id}/audit", response_model=AuditClubResponse)
def audit_club(
    club_id: int,
    data: AuditClubRequest,
    session: Session = Depends(get_session),
):
    """
    审核社团（管理员功能）

    - 通过审核：将社团状态改为 ACTIVE
    - 拒绝审核：将社团状态改为 INACTIVE，需填写拒绝原因
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查社团当前状态是否为待审核
    if club.status != "REVIEW":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"社团当前状态为 {club.status}，无法审核",
        )

    # 拒绝时必须填写原因
    if not data.approved and not data.reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="拒绝审核时必须填写拒绝原因",
        )

    # 更新社团状态
    club_repo.audit_club(
        session,
        club=club,
        approved=data.approved,
        reason=data.reason,
    )

    return AuditClubResponse(detail="社团审核完成")


@router.get("/{club_id}/members", response_model=ClubMembersResponse)
def get_club_members(
    club_id: int,
    session: Session = Depends(get_session),
):
    """
    获取社团成员列表

    - 返回所有与该社团关联的用户及其角色
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 获取社团成员
    members = club_repo.get_club_members(session, club_id)

    return ClubMembersResponse(
        items=[ClubMemberItem(**member) for member in members["items"]],
        total=members["total"],
    )


@router.put("/{club_id}/members/{user_id}/role", response_model=UpdateMemberRoleResponse)
def update_member_role(
    club_id: int,
    user_id: int,
    data: UpdateMemberRoleRequest,
    session: Session = Depends(get_session),
):
    """
    更新社团成员角色

    - 修改成员在社团中的角色
    """
    user_repo = UserAccountRepository()
    role_repo = RoleRepository()
    user_role_repo = UserRoleRepository()

    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查用户是否存在
    user = user_repo.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 检查角色是否存在
    role = role_repo.get(session, data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )

    # 检查用户是否是该社团成员
    existing = user_role_repo.get_by_user_role_club(
        session,
        user_id=user_id,
        role_id=data.role_id,
        club_id=club_id,
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不是该社团成员",
        )

    # 更新角色
    user_role_repo.update_user_role(
        session,
        user_role=existing,
        new_role_id=data.role_id,
        new_club_id=data.club_id,
    )

    return UpdateMemberRoleResponse(detail="成员角色已更新")


@router.delete("/{club_id}/members/{user_id}", response_model=RemoveMemberResponse)
def remove_member(
    club_id: int,
    user_id: int,
    data: RemoveMemberRequest,
    session: Session = Depends(get_session),
):
    """
    移除社团成员

    - 将成员从社团中移除（软删除 user_role 记录）
    """
    user_repo = UserAccountRepository()
    user_role_repo = UserRoleRepository()

    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 检查用户是否存在
    user = user_repo.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 获取用户在该社团的所有角色
    user_roles = user_role_repo.get_by_user_and_club(
        session,
        user_id=user_id,
        club_id=club_id,
    )

    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不是该社团成员",
        )

    # 移除所有角色
    for user_role in user_roles:
        user_role_repo.soft_delete(session, user_role)

    return RemoveMemberResponse(detail="成员已移除")


@router.delete("/{club_id}/interviewers/{user_id}", response_model=RemoveMemberResponse)
def remove_interviewer(
    club_id: int,
    user_id: int,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    删除社团面试官角色

    - 只移除 INTERVIEWER 角色
    - 不影响该用户在同社团下的其他角色（如 CLUB_ADMIN）
    """
    user_repo = UserAccountRepository()
    role_repo = RoleRepository()
    user_role_repo = UserRoleRepository()

    _ensure_club_admin(session, current_user, club_id)

    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    user = user_repo.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    interviewer_role = role_repo.get_by_code(session, "INTERVIEWER")
    if not interviewer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    interviewer_relation = user_role_repo.get_by_user_role_club(
        session,
        user_id=user_id,
        role_id=interviewer_role.id,
        club_id=club_id,
    )
    if not interviewer_relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该用户不是本社团面试官",
        )

    removal_record = InterviewerInvitation(
        club_id=club_id,
        user_id=user_id,
        invite_code=f"REMOVED-{uuid4().hex[:16].upper()}",
        status="REMOVED",
        inviter_id=current_user.id,
    )
    session.add(removal_record)
    session.flush()

    notification = Notification(
        type="INTERVIEWER_REMOVED",
        title=f"您已被移出 {club.name} 面试官",
        content=f"社团“{club.name}”已移除您的面试官权限。",
        biz_id=removal_record.id,
        sent_at=removal_record.created_at,
        status="SENT",
    )
    session.add(notification)
    session.flush()
    session.add(NotificationUser(
        notification_id=notification.id,
        user_id=user_id,
        read_status="UNREAD",
    ))

    user_role_repo.soft_delete(session, interviewer_relation)

    return RemoveMemberResponse(detail="面试官已移除")


@router.get("/{club_id}/stats", response_model=ClubStatsResponse)
def get_club_stats(
    club_id: int,
    session: Session = Depends(get_session),
):
    """
    获取社团统计数据

    - 成员总数
    - 活跃岗位数
    - 活跃招新场次数
    - 报名总数
    - 面试总数
    - 待审核报名数
    - 即将到来的面试数
    """
    # 检查社团是否存在
    club = club_repo.get(session, club_id)
    if not club or club.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社团不存在",
        )

    # 获取统计数据
    stats = club_repo.get_club_stats(session, club_id)

    return ClubStatsResponse(**stats)
