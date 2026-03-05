from pydantic import BaseModel, Field
from typing import Optional, List


# ============ 用户角色相关 ============

class AssignRoleRequest(BaseModel):
    """分配角色请求"""
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    club_id: Optional[int] = Field(default=None, description="社团ID（面试官/管理角色需要）")


class RevokeRoleRequest(BaseModel):
    """撤销角色请求"""
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    club_id: Optional[int] = Field(default=None, description="社团ID")


class UserRoleResponse(BaseModel):
    """用户角色响应"""
    id: int
    user_id: int
    role_id: int
    club_id: Optional[int] = None


class AssignRoleResponse(BaseModel):
    """分配角色响应"""
    detail: str = "角色分配成功"
    user_role: UserRoleResponse


class RevokeRoleResponse(BaseModel):
    """撤销角色响应"""
    detail: str = "角色撤销成功"


class UserRoleInfo(BaseModel):
    """用户角色信息"""
    id: int
    code: str
    name: str
    club_id: Optional[int] = None


class AuthMeResponse(BaseModel):
    """当前用户信息响应（包含角色列表）"""
    id: int
    phone: str
    name: str | None
    status: int
    is_initialized: bool
    school_code: str | None = None
    school_name: str | None = None
    roles: List[UserRoleInfo] = []


# ============ 验证码相关 ============

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., min_length=6, max_length=20, description="手机号")
    scene: str = Field(..., description="场景：REGISTER / LOGIN")


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    detail: str = "验证码已发送"


class InitAccountRequest(BaseModel):
    """账号初始化请求（登录后调用）"""
    # bcrypt 建议 <= 72 bytes，这里先限制长度，避免你之前遇到的报错
    password: str = Field(..., min_length=6, max_length=72, description="密码")

    # 实名信息
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    id_card_no: str = Field(..., min_length=15, max_length=32, description="身份证号")

    # 学籍信息
    school_code: str = Field(..., description="学校标识码")
    major: str = Field(..., min_length=1, max_length=100, description="专业")
    student_no: str = Field(..., min_length=1, max_length=50, description="学号")

    # 可选信息
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    avatar_url: Optional[str] = Field(default=None, max_length=255, description="头像URL")


class InitAccountResponse(BaseModel):
    detail: str = "账号初始化成功"


class RegisterRequest(BaseModel):
    """注册请求（仅手机号+验证码，密码等在初始化接口填写）"""
    phone: str = Field(..., min_length=6, max_length=20, description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="6位验证码")
