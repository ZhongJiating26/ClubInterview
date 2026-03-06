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


# ============ 社团管理增强相关 ============

class ClubListRequest(BaseModel):
    """社团列表查询请求"""
    school_code: Optional[str] = Field(default=None, description="学校标识码")
    status: Optional[str] = Field(default=None, description="社团状态（ACTIVE/INACTIVE/REVIEW）")
    category: Optional[str] = Field(default=None, description="社团分类")
    keyword: Optional[str] = Field(default=None, description="搜索关键词（社团名称）")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class ClubListItem(BaseModel):
    """社团列表项"""
    id: int
    school_name: str
    name: str
    logo_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: str


class ClubListResponse(BaseModel):
    """社团列表响应"""
    items: list[ClubListItem]
    total: int
    page: int
    page_size: int


class AuditClubRequest(BaseModel):
    """社团审核请求"""
    approved: bool = Field(..., description="是否通过审核")
    reason: Optional[str] = Field(default=None, description="拒绝原因（approved=False 时必填）")


class AuditClubResponse(BaseModel):
    """社团审核响应"""
    detail: str = "社团审核完成"


class ClubMemberItem(BaseModel):
    """社团成员列表项"""
    user_id: int
    user_name: str
    user_phone: str
    role_id: int
    role_name: str
    club_id: int
    joined_at: str


class ClubMembersResponse(BaseModel):
    """社团成员列表响应"""
    items: list[ClubMemberItem]
    total: int


class UpdateMemberRoleRequest(BaseModel):
    """更新成员角色请求"""
    role_id: int = Field(..., description="新角色ID")
    club_id: Optional[int] = Field(default=None, description="社团ID（角色关联的社团）")


class UpdateMemberRoleResponse(BaseModel):
    """更新成员角色响应"""
    detail: str = "成员角色已更新"


class RemoveMemberRequest(BaseModel):
    """移除成员请求"""
    reason: Optional[str] = Field(default=None, description="移除原因")


class RemoveMemberResponse(BaseModel):
    """移除成员响应"""
    detail: str = "成员已移除"


class ClubStatsResponse(BaseModel):
    """社团统计数据响应"""
    club_id: int
    club_name: str
    total_members: int  # 总成员数
    active_positions: int  # 活跃岗位数
    active_recruitments: int  # 活跃招新场次数
    total_applications: int  # 总报名数
    total_interviews: int  # 总面试数
    pending_reviews: int  # 待审核报名数
    upcoming_interviews: int  # 即将到来的面试数
