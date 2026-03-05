from typing import Optional
from pydantic import BaseModel, Field


class InitClubRequest(BaseModel):
    """初始化社团请求（在用户信息初始化时调用）"""
    club_name: str = Field(..., min_length=1, max_length=100, description="社团名称")
    school_code: str = Field(..., description="学校标识码")


class InitClubResponse(BaseModel):
    """初始化社团响应"""
    detail: str = "社团初始化成功"
    club_id: int
    is_new: bool  # True-新创建，False-已存在


class UpdateClubRequest(BaseModel):
    """完善/修改社团信息请求"""
    name: Optional[str] = Field(default=None, max_length=100, description="社团名称")
    logo_url: Optional[str] = Field(default=None, max_length=255, description="LOGO 存储路径")
    category: Optional[str] = Field(default=None, max_length=50, description="社团分类（技术/文艺等）")
    description: Optional[str] = Field(default=None, description="社团介绍")


class ClubResponse(BaseModel):
    """社团信息响应"""
    id: int
    school_name: str
    name: str
    logo_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    cert_file_url: Optional[str] = None
    status: str
    created_at: str


class ClubProfileCheckResponse(BaseModel):
    """社团资料完善度检查响应"""
    club_id: int
    is_complete: bool
    missing_fields: list[str] = []


class CheckClubRequest(BaseModel):
    """检查社团是否存在请求"""
    club_name: str = Field(..., min_length=1, max_length=100, description="社团名称")
    school_code: str = Field(..., description="学校标识码")


class CheckClubResponse(BaseModel):
    """检查社团是否存在响应"""
    exists: bool
    club_id: int | None = None
    message: str = ""


class BindUserRequest(BaseModel):
    """关联用户到社团请求"""
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(default=2, description="角色ID (默认 2=CLUB_ADMIN)")


class BindUserResponse(BaseModel):
    """关联用户到社团响应"""
    detail: str = "用户已关联到社团"


class HomeClubItem(BaseModel):
    """首页社团列表项"""
    id: int
    name: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    school_name: str
    status: str
    recruiting_status: str  # "RECRUITING" 或 "NO_RECRUITMENT"


class ClubDetailResponse(BaseModel):
    """社团详情响应（完整信息）"""
    # 社团基本信息
    id: int
    school_name: str
    name: str
    logo_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    cert_file_url: Optional[str] = None
    status: str
    created_at: str

    # 部门列表
    departments: list[dict] = []

    # 岗位列表
    positions: list[dict] = []

    # 招新场次列表
    recruitment_sessions: list[dict] = []
