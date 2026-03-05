from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session

from app.db.session import get_session
from app.models.club import Club
from app.models.user_role import UserRole
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
)


router = APIRouter(prefix="/clubs", tags=["Club"])
club_repo = ClubRepository()
dept_repo = DepartmentRepository()
position_repo = ClubPositionRepository()
session_repo = RecruitmentSessionRepository()
session_position_repo = RecruitmentSessionPositionRepository()


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
