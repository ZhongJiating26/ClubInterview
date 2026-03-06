import random
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.models.user_account import UserAccount
from app.db.session import get_session
from app.repositories.user_account import UserAccountRepository
from app.repositories.role import RoleRepository
from app.repositories.verification_code import VerificationCodeRepository
from app.core.security import create_access_token
from app.schemas.auth import (
    InitAccountRequest, InitAccountResponse, AuthMeResponse, UserRoleInfo,
    SendCodeRequest, SendCodeResponse, RegisterRequest,
    LoginRequest, LoginResponse,
    AssignRoleRequest,
    AssignRoleResponse, UserRoleResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    DeleteAccountRequest, DeleteAccountResponse,
)


router = APIRouter(prefix="/auth", tags=["Auth"])
user_repo = UserAccountRepository()
role_repo = RoleRepository()
verify_code_repo = VerificationCodeRepository()

# 验证码有效期（分钟）
CODE_EXPIRE_MINUTES = 5


def generate_code() -> str:
    """生成6位数字验证码"""
    return f"{random.randint(100000, 999999)}"


@router.post("/send-code", response_model=SendCodeResponse)
def send_code(
    data: SendCodeRequest,
    session: Session = Depends(get_session),
):
    """
    发送验证码
    - REGISTER 场景：手机号已存在且已完成初始化则报错；仅注册未完善资料可以继续
    - LOGIN 场景：手机号不存在则报错
    注意：当前为开发模式，无论手机号如何，返回验证码
    """
    # 检查手机号是否已注册
    existing_user = user_repo.get_by_phone(session, data.phone)

    if data.scene == "REGISTER":
        # 注册场景：手机号已存在且已完成初始化不能发送验证码
        if existing_user and existing_user.password_hash is not None:
            raise HTTPException(
                status_code=400,
                detail="手机号已注册",
            )
    elif data.scene == "LOGIN":
        # 登录场景：手机号不存在不能发送验证码
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="手机号未注册",
            )

    # 生成验证码
    code = generate_code()
    expired_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)

    # 标记旧的验证码为已删除
    verify_code_repo.delete_expired_codes(session, data.phone, data.scene)

    # 创建新的验证码记录
    verify_code_repo.create_code(
        session=session,
        phone=data.phone,
        code=code,
        scene=data.scene,
        expired_at=expired_at,
    )

    # TODO: 后续接入短信服务时，在此调用发送短信接口

    return SendCodeResponse(detail="验证码已发送")


@router.post("/register", response_model=LoginResponse)
def register(
    data: RegisterRequest,
    session: Session = Depends(get_session),
):
    """
    注册账号（仅手机号+验证码，密码等在初始化接口填写）
    注册成功后返回 access_token，用户可直接进入初始化页面
    注意：当前为开发模式，验证码无论输入什么都正确
    """
    # 1️⃣ 校验验证码（开发模式：跳过校验）
    # 正式环境应取消注释以下代码：
    # valid_code = verify_code_repo.get_valid_code(
    #     session, data.phone, data.code, "REGISTER"
    # )
    # if not valid_code:
    #     raise HTTPException(status_code=400, detail="验证码无效或已过期")
    # verify_code_repo.mark_as_used(session, valid_code)

    # 2️⃣ 检查手机号是否已注册
    existing = user_repo.get_by_phone(session, data.phone)

    if existing:
        # 手机号已存在，检查是否已完成初始化
        if existing.password_hash is not None:
            # 已完成初始化，不允许重复注册
            raise HTTPException(
                status_code=400,
                detail="手机号已注册",
            )
        # 未完成初始化（仅注册未完善资料），直接使用现有用户重新走初始化流程
        user = existing
    else:
        # 3️⃣ 创建新用户（仅手机号，其他信息在初始化接口填写）
        user = user_repo.create_user(
            session,
            phone=data.phone,
            password="",  # 初始密码为空，需要通过 init 接口设置
        )

    # 4️⃣ 签发 JWT（注册用户也可获得 token，用于跳转初始化页面）
    token_payload = {
        "user_id": user.id,
        "token_version": user.token_version,
    }
    access_token = create_access_token(subject=token_payload)

    return LoginResponse(access_token=access_token)


@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
):
    # 1️⃣ 查用户
    user = user_repo.get_by_phone(session, data.phone)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="手机号或密码错误",
        )

    # 2️⃣ 校验状态
    if user.status != 1:
        raise HTTPException(
            status_code=403,
            detail="用户已被禁用",
        )

    # ⭐ 2.5️⃣ 账号是否初始化（新增，关键）
    if user.password_hash is None:
        raise HTTPException(
            status_code=403,
            detail="账号尚未初始化，请先完善账号信息",
        )

    # 3️⃣ 校验密码
    if not user_repo.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="手机号或密码错误",
        )

    # 4️⃣ 签发 JWT（带 token_version）
    token_payload = {
        "user_id": user.id,
        "token_version": user.token_version,
    }

    access_token = create_access_token(subject=token_payload)
    return LoginResponse(access_token=access_token)


@router.get("/me", response_model=AuthMeResponse)
def me(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # 获取用户角色列表
    from app.models.user_role import UserRole
    from sqlmodel import select
    from app.repositories.school import SchoolRepository

    school_repo = SchoolRepository()

    stmt = (
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.is_deleted == 0)
    )
    user_roles = session.execute(stmt).scalars().all()

    # 获取角色详情
    roles = []
    for ur in user_roles:
        role = role_repo.get(session, ur.role_id)
        if role:
            roles.append(UserRoleInfo(
                id=role.id,
                code=role.code,
                name=role.name,
                club_id=ur.club_id,
            ))

    # 获取学校名称
    school_name = None
    if current_user.school_code:
        school = school_repo.get_by_code(session, current_user.school_code)
        if school:
            school_name = school.name

    return AuthMeResponse(
        id=current_user.id,
        phone=current_user.phone,
        name=current_user.name,
        status=current_user.status,
        is_initialized=current_user.password_hash is not None,
        school_code=current_user.school_code,
        school_name=school_name,
        roles=roles,
    )


@router.post("/init", response_model=InitAccountResponse)
def init_account(
    data: InitAccountRequest,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    初始化账号（设置密码和个人信息）
    需要用户已登录
    """
    # 1) 禁用用户不能操作
    if current_user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 2) 已初始化不能重复初始化
    if current_user.password_hash is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="账号已初始化，无需重复初始化",
        )

    # 3) 执行初始化（写入密码 + 资料）
    user_repo.init_account(
        session,
        user=current_user,
        password=data.password,
        name=data.name,
        id_card_no=data.id_card_no,
        school_code=data.school_code,
        major=data.major,
        student_no=data.student_no,
        email=data.email,
        avatar_url=data.avatar_url,
    )

    return InitAccountResponse(detail="账号初始化成功")


# ============ 用户角色管理 ============

from app.repositories.user_role import UserRoleRepository

user_role_repo = UserRoleRepository()


@router.post("/assign-role", response_model=AssignRoleResponse)
def assign_role(
    data: AssignRoleRequest,
    session: Session = Depends(get_session),
):
    """
    为用户分配角色（根据角色ID）
    """
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

    # 分配角色
    user_role = user_role_repo.assign_role(
        session,
        user_id=data.user_id,
        role_id=data.role_id,
        club_id=data.club_id,
    )

    return AssignRoleResponse(
        detail="角色分配成功",
        user_role=UserRoleResponse(
            id=user_role.id,
            user_id=user_role.user_id,
            role_id=user_role.role_id,
            club_id=user_role.club_id,
        ),
    )


# ============ 密码管理功能 ============


@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password(
    data: ChangePasswordRequest,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    修改密码
    - 需要验证旧密码
- 修改成功后会使所有 Token 失效（通过增加 token_version）
    """
    # 1️⃣ 验证旧密码
    if not user_repo.verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )

    # 2️⃣ 检查新密码是否与旧密码相同
    if user_repo.verify_password(data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同",
        )

    # 3️⃣ 更新密码（同时增加 token_version 使旧 Token 失效）
    user_repo.change_password(session, current_user, data.new_password)

    return ChangePasswordResponse(detail="密码修改成功，请重新登录")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    data: ForgotPasswordRequest,
    session: Session = Depends(get_session),
):
    """
    忘记密码（发送验证码）
    - 验证手机号是否已注册
- 发送验证码到手机号
    """
    # 1️⃣ 检查手机号是否已注册
    user = user_repo.get_by_phone(session, data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手机号未注册",
        )

    # 2️⃣ 检查用户状态
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 3️⃣ 生成验证码
    code = generate_code()
    expired_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)

    # 4️⃣ 标记旧的验证码为已删除
    verify_code_repo.delete_expired_codes(session, data.phone, "RESET_PASSWORD")

    # 5️⃣ 创建新的验证码记录
    verify_code_repo.create_code(
        session=session,
        phone=data.phone,
        code=code,
        scene="RESET_PASSWORD",
        expired_at=expired_at,
    )

    # TODO: 后续接入短信服务时，在此调用发送短信接口

    return ForgotPasswordResponse(detail="验证码已发送")


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    data: ResetPasswordRequest,
    session: Session = Depends(get_session),
):
    """
    重置密码
    - 使用验证码验证身份
    - 重置成功后可以使用新密码登录
    """
    # 1️⃣ 检查手机号是否已注册
    user = user_repo.get_by_phone(session, data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手机号未注册",
        )

    # 2️⃣ 检查用户状态
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 3️⃣ 校验验证码
    # 开发模式：跳过验证码校验
    # 正式环境应取消注释以下代码：
    # valid_code = verify_code_repo.get_valid_code(
    #     session, data.phone, data.code, "RESET_PASSWORD"
    # )
    # if not valid_code:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="验证码无效或已过期",
    #     )
    # verify_code_repo.mark_as_used(session, valid_code)

    # 4️⃣ 更新密码（同时增加 token_version 使旧 Token 失效）
    user_repo.change_password(session, user, data.new_password)

    return ResetPasswordResponse(detail="密码重置成功，请使用新密码登录")


@router.post("/account/delete", response_model=DeleteAccountResponse)
def delete_account(
    data: DeleteAccountRequest,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    注销账号
    - 需要验证密码
    - 需要输入确认文本 'DELETE'
    - 软删除账号（is_deleted = 1）
    - 注销后无法恢复，请谨慎操作
    """
    # 1️⃣ 验证密码
    if not user_repo.verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误",
        )

    # 2️⃣ 验证确认文本
    if data.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入 'DELETE' 确认注销账号",
        )

    # 3️⃣ 软删除账号
    user_repo.soft_delete(session, current_user)

    return DeleteAccountResponse(detail="账号已注销")
