from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 通用响应 ====================

class ApiResponse(BaseModel):
    """通用 API 响应"""
    code: int = 200
    message: str = ""


class ApplicationCreate(BaseModel):
    """创建报名请求"""
    recruitment_session_id: int = Field(..., description="招新场次ID")
    position_ids: List[int] = Field(..., description="岗位ID列表")
    self_intro: Optional[str] = Field(default=None, description="自我介绍")
    extra_fields: Optional[dict] = Field(default=None, description="额外字段")


class ApplicationUpdate(BaseModel):
    """更新报名请求"""
    self_intro: Optional[str] = Field(default=None, description="自我介绍")
    items: Optional[List[dict]] = Field(default=None, description="报名岗位列表")


class ApplicationResponse(BaseModel):
    """报名响应"""
    id: int
    user_id: int
    recruitment_session_id: int
    self_intro: Optional[str] = None
    status: str
    audit_user_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SignupSubmitData(BaseModel):
    """报名提交响应数据"""
    signup_id: int
    status: str


class SignupSubmitResponse(ApiResponse):
    """报名提交响应"""
    data: SignupSubmitData


class SignupItemData(BaseModel):
    """报名岗位数据"""
    id: int
    signup_session_id: int
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    position_id: int
    position_name: Optional[str] = None


class SignupApplicationData(BaseModel):
    """报名申请数据"""
    id: int
    user_id: int
    recruitment_session_id: int
    session_name: Optional[str] = None
    self_intro: Optional[str] = None
    status: str
    audit_time: Optional[datetime] = None
    audit_reason: Optional[str] = None
    created_at: datetime
    items: List[SignupItemData] = []


class SignupApplicationListData(BaseModel):
    """报名申请列表数据"""
    items: List[SignupApplicationData]
    total: int


class SignupApplicationListResponse(ApiResponse):
    """报名申请列表响应"""
    data: SignupApplicationListData


# ==================== 学生端报名列表响应（新规范）====================

class SignupApplicationItemData(BaseModel):
    """报名岗位数据（响应）"""
    id: int
    signup_session_id: int
    department_id: Optional[int] = None
    position_id: int


class SignupApplicationListResponse2(BaseModel):
    """报名记录列表响应（新规范）"""
    items: List[SignupApplicationData] = []
    total: int


class SignupApplicationDetailData(BaseModel):
    """报名详情数据（新规范）"""
    id: int
    user_id: int
    recruitment_session_id: int
    session_name: Optional[str] = None
    self_intro: Optional[str] = None
    status: str
    audit_user_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[dict] = []
    attachments: List[dict] = []


# ==================== 面试相关 ====================

class InterviewResponse(BaseModel):
    """面试响应"""
    id: int
    session_id: int
    signup_session_id: Optional[int] = None
    candidate_user_id: int
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: str
    final_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class InterviewConfirmationUpdate(BaseModel):
    """面试确认更新"""
    status: str = Field(..., description="状态：CONFIRMED / DECLINED")


class InterviewResultResponse(BaseModel):
    """面试结果响应"""
    passed: bool
    score: Optional[float] = None
    feedback: Optional[str] = None
    admission_result: Optional[str] = None


# ==================== 学生端面试记录响应（新规范）====================

class StudentInterviewRecordData(BaseModel):
    """学生面试记录数据（新规范）"""
    id: int
    session_id: int
    signup_application_id: Optional[int] = None
    user_id: int
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    position_id: Optional[int] = None
    position_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: str
    final_score: Optional[float] = None
    created_at: datetime


class InterviewSessionInfoData(BaseModel):
    """面试场次信息数据"""
    id: int
    name: str
    place: Optional[str] = None
    start_time: datetime
    end_time: datetime


class SignupApplicationInfoData(BaseModel):
    """报名申请信息数据"""
    id: int
    recruitment_session_id: int
    session_name: Optional[str] = None
    status: str
    self_intro: Optional[str] = None
    created_at: datetime


class StudentInterviewRecordDetailData(BaseModel):
    """学生面试记录详情数据（新规范）"""
    id: int
    session_id: int
    signup_application_id: Optional[int] = None
    user_id: int
    user_name: Optional[str] = None
    position_id: Optional[int] = None
    position_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: str
    final_score: Optional[float] = None
    created_at: datetime
    session: Optional[InterviewSessionInfoData] = None
    application: Optional[SignupApplicationInfoData] = None


# ==================== 通知相关 ====================

class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    type: str
    title: str
    content: str
    biz_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    created_at: datetime


class NotificationUnreadCountResponse(BaseModel):
    """未读通知数量响应"""
    count: int


# ==================== 工单相关 ====================

class TicketCreate(BaseModel):
    """创建工单请求"""
    title: str = Field(..., min_length=1, max_length=255, description="工单标题")
    content: str = Field(..., description="工单内容")
    category: str = Field(..., description="工单分类")
    club_id: Optional[int] = Field(default=None, description="关联社团ID（可选）")


class TicketMessageCreate(BaseModel):
    """工单回复请求"""
    content: str = Field(..., description="回复内容")
    attachment_url: Optional[str] = Field(default=None, description="附件URL")


class TicketResponse(BaseModel):
    """工单响应"""
    id: int
    user_id: int
    club_id: Optional[int] = None
    title: str
    category: str
    content: str
    status: str
    priority: str
    assignee_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # 回复列表
    replies: List[dict] = []


class TicketReplyResponse(BaseModel):
    """工单回复响应"""
    id: int
    ticket_id: int
    user_id: int
    content: str
    is_from_staff: bool
    attachment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ==================== 个人中心相关 ====================

class StudentProfileResponse(BaseModel):
    """学生个人资料响应"""
    id: int
    phone: str
    name: Optional[str] = None
    id_card_no: Optional[str] = None
    school_code: Optional[str] = None
    major: Optional[str] = None
    student_no: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    is_verified_campus: bool = False
    created_at: datetime
    updated_at: datetime


class ProfileData(BaseModel):
    """用户资料数据（新格式）"""
    id: int
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    student_no: Optional[str] = None
    major: Optional[str] = None
    school_code: Optional[str] = None
    school_name: Optional[str] = None
    status: int
    is_initialized: bool
    avatar_url: Optional[str] = None


class ProfileResponse(ApiResponse):
    """用户资料响应（新格式）"""
    data: ProfileData


class StudentProfileUpdate(BaseModel):
    """更新学生个人资料请求"""
    name: Optional[str] = Field(default=None, max_length=100, description="姓名")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    major: Optional[str] = Field(default=None, max_length=100, description="专业")


class ApplicationStatsResponse(BaseModel):
    """报名统计响应"""
    total: int
    pending: int
    approved: int
    rejected: int


# ==================== FAQ相关 ====================

class FAQResponse(BaseModel):
    """FAQ响应"""
    id: int
    club_id: Optional[int] = None
    category: str
    question: str
    answer: str
    order_no: int
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime
