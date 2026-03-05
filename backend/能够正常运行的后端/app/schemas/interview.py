from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class InterviewSessionInterviewerCreate(BaseModel):
    """添加面试官到场次请求"""
    interviewer_id: int = Field(..., description="面试官记录ID（user_role表的id）")


class InterviewSessionInterviewerResponse(BaseModel):
    """面试场次-面试官关联响应"""
    id: int
    session_id: int
    interviewer_id: int
    role: str
    created_at: datetime


class SessionInterviewerResponse(BaseModel):
    """场次面试官列表响应（包含用户信息）"""
    id: int
    user_id: int
    club_id: int
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None


class InterviewSessionScoreItemCreate(BaseModel):
    """添加评分项到场次请求"""
    score_item_id: int = Field(..., description="评分项ID")
    order_no: int = Field(..., ge=1, description="排序")


class InterviewSessionScoreItemResponse(BaseModel):
    """面试场次-评分项关联响应"""
    id: int
    session_id: int
    score_item_id: int
    order_no: int
    created_at: datetime


class SetScoreItemsRequest(BaseModel):
    """设置场次评分项列表请求"""
    score_item_ids: List[int] = Field(..., min_length=1, description="评分项ID列表（按顺序）")


class InterviewSessionCreate(BaseModel):
    """创建面试场次请求"""
    recruitment_session_id: int = Field(..., description="招新场次ID")
    name: str = Field(..., min_length=1, max_length=100, description="场次名称")
    description: Optional[str] = Field(default=None, description="描述")
    place: Optional[str] = Field(default=None, max_length=255, description="面试地点")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    status: Optional[str] = Field(default="DRAFT", description="状态：DRAFT / OPEN / CLOSED")


class InterviewSessionUpdate(BaseModel):
    """更新面试场次请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="场次名称")
    description: Optional[str] = Field(default=None, description="描述")
    place: Optional[str] = Field(default=None, max_length=255, description="面试地点")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    status: Optional[str] = Field(default=None, description="状态：DRAFT / OPEN / CLOSED")


class InterviewSessionResponse(BaseModel):
    """面试场次响应"""
    id: int
    club_id: int
    recruitment_session_id: int
    name: str
    description: Optional[str] = None
    place: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class InterviewSessionListResponse(BaseModel):
    """面试场次列表响应（包含统计字段）"""
    id: int
    club_id: int
    recruitment_session_id: int
    name: str
    description: Optional[str] = None
    place: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    interviewer_count: Optional[int] = None
    candidate_count: Optional[int] = None


class InterviewCandidateCreate(BaseModel):
    """创建候选人排期请求"""
    session_id: int = Field(..., description="场次ID")
    signup_session_id: Optional[int] = Field(default=None, description="报名ID")
    candidate_user_id: int = Field(..., description="用户ID")
    planned_start_time: Optional[datetime] = Field(default=None, description="计划开始时间")
    planned_end_time: Optional[datetime] = Field(default=None, description="计划结束时间")


class GenerateCandidatesRequest(BaseModel):
    """生成候选人排期请求"""
    signup_application_ids: Optional[List[int]] = Field(default=None, description="指定报名ID列表")
    time_slot_duration: Optional[int] = Field(default=60, description="每个时间槽时长（分钟），默认60")
    start_time: Optional[datetime] = Field(default=None, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")


class InterviewCandidateResponse(BaseModel):
    """候选人排期响应"""
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


class InterviewCandidateDetailResponse(BaseModel):
    """候选人排期详情响应（包含用户和报名信息）"""
    id: int
    session_id: int
    signup_session_id: Optional[int] = None
    candidate_user_id: int
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


class SignupSessionInfo(BaseModel):
    """报名信息"""
    id: int
    user_id: int
    recruitment_session_id: int
    status: str
    self_intro: Optional[str] = None


class InterviewCandidateWithApplicationResponse(BaseModel):
    """候选人详情响应（包含完整报名信息）"""
    id: int
    session_id: int
    signup_session_id: Optional[int] = None
    candidate_user_id: int
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
    application: Optional[SignupSessionInfo] = None


class InterviewRecordCreate(BaseModel):
    """创建面试记录请求"""
    session_id: int = Field(..., description="场次ID")
    candidate_user_id: int = Field(..., description="学生ID")
    summary: Optional[str] = Field(default=None, description="总结")
    record_text: Optional[str] = Field(default=None, description="手写记录")


class InterviewRecordUpdate(BaseModel):
    """更新面试记录请求"""
    summary: Optional[str] = Field(default=None, description="总结")
    record_text: Optional[str] = Field(default=None, description="手写记录")
    recording_url: Optional[str] = Field(default=None, description="录音URL")
    face_image_url: Optional[str] = Field(default=None, description="照片URL")


class InterviewRecordResponse(BaseModel):
    """面试记录响应"""
    id: int
    session_id: int
    signup_session_id: Optional[int] = None
    candidate_user_id: int
    interviewer_id: int
    status: str
    total_score: Optional[float] = None
    summary: Optional[str] = None
    record_text: Optional[str] = None
    recording_url: Optional[str] = None
    face_image_url: Optional[str] = None
    transcript_status: str
    transcript_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ScoreItemCreate(BaseModel):
    """创建评分项请求"""
    name: str = Field(..., min_length=1, max_length=100, description="评分项名称")
    weight: int = Field(..., ge=1, description="权重")
    max_score: float = Field(..., gt=0, description="满分")
    order_no: int = Field(..., ge=1, description="排序")


class ScoreItemResponse(BaseModel):
    """评分项响应"""
    id: int
    template_id: Optional[int] = None
    session_id: Optional[int] = None
    name: str
    weight: int
    max_score: float
    order_no: int
    created_at: datetime
    updated_at: datetime


class InterviewScoreCreate(BaseModel):
    """创建评分请求"""
    score_item_id: int = Field(..., description="评分项ID")
    score: float = Field(..., ge=0, description="得分")
    remark: Optional[str] = Field(default=None, max_length=255, description="备注")


class InterviewScoreResponse(BaseModel):
    """评分明细响应"""
    id: int
    record_id: int
    score_item_id: int
    item_name: str
    item_weight: int
    item_max_score: float
    score: float
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdmissionResultUpdate(BaseModel):
    """更新录取结果请求"""
    result: str = Field(..., description="录取结果：PASS / REJECT / WAITLIST")
    department_id: Optional[int] = Field(default=None, description="录取所属部门ID")
    position_id: Optional[int] = Field(default=None, description="录取岗位ID")
    remark: Optional[str] = Field(default=None, max_length=255, description="备注")


class AdmissionResultResponse(BaseModel):
    """录取结果响应"""
    id: int
    interview_candidate_id: Optional[int] = None
    signup_session_id: Optional[int] = None
    candidate_user_id: int
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    result: str
    final_score_snapshot: Optional[float] = None
    decided_by: Optional[int] = None
    decided_at: Optional[datetime] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AssignableInterviewerResponse(BaseModel):
    """可分配的面试官响应"""
    id: int = Field(..., description="面试官记录 ID（user_role 表的 id）")
    user_id: int = Field(..., description="用户 ID")
    name: Optional[str] = Field(None, description="姓名")
    phone: str = Field(..., description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    role: str = Field(..., description="角色：CLUB_ADMIN 或 INTERVIEWER")


# ==================== 评分模板相关 ====================

class ScoreTemplateResponse(BaseModel):
    """评分模板响应"""
    id: int
    club_id: int
    name: str
    description: Optional[str] = None
    is_default: bool = False
    created_at: datetime
    updated_at: datetime


class ScoreItemDetailResponse(BaseModel):
    """评分项详情响应"""
    id: int
    template_id: Optional[int] = None
    session_id: Optional[int] = None
    title: str = Field(..., description="评分项标题")
    description: Optional[str] = None
    max_score: float
    weight: int
    sort_order: int


class SetScoreTemplateRequest(BaseModel):
    """设置场次评分模板请求"""
    template_id: Optional[int] = Field(None, description="模板ID（使用已有模板）")
    custom_items: Optional[List[dict]] = Field(None, description="自定义评分项列表")


class SetScoreTemplateCustomItem(BaseModel):
    """自定义评分项"""
    title: str = Field(..., description="评分项标题")
    description: Optional[str] = Field(None, description="描述")
    max_score: float = Field(..., gt=0, description="满分")
    weight: int = Field(..., ge=1, description="权重")
