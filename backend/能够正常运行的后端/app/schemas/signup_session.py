from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_serializer


class SignupSubmitItem(BaseModel):
    """报名时选择的岗位"""
    department_id: Optional[int] = Field(default=None, description="部门ID")
    position_id: int = Field(..., description="岗位ID")


class SignupSubmitRequest(BaseModel):
    """提交报名请求"""
    recruitment_session_id: int = Field(..., description="招新场次ID")
    self_intro: Optional[str] = Field(default=None, description="自我介绍")
    positions: List[SignupSubmitItem] = Field(..., min_length=1, description="报名的岗位列表")


class SignupItemResponse(BaseModel):
    """报名岗位响应"""
    id: int
    signup_session_id: int
    department_id: Optional[int] = None
    position_id: int

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "signup_session_id": self.signup_session_id,
            "department_id": self.department_id,
            "position_id": self.position_id,
        }

    class Config:
        from_attributes = True


class SignupAttachmentResponse(BaseModel):
    """报名附件响应"""
    id: int
    signup_session_id: int
    file_url: str
    file_type: str
    file_name: str
    file_size: Optional[int] = None
    created_at: datetime

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "signup_session_id": self.signup_session_id,
            "file_url": self.file_url,
            "file_type": self.file_type,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
        }

    class Config:
        from_attributes = True


class SignupSessionResponse(BaseModel):
    """报名详情响应"""
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
    items: List[SignupItemResponse] = []
    attachments: List[SignupAttachmentResponse] = []

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recruitment_session_id": self.recruitment_session_id,
            "self_intro": self.self_intro,
            "status": self.status,
            "audit_user_id": self.audit_user_id,
            "audit_time": self.audit_time.isoformat() if self.audit_time else None,
            "audit_reason": self.audit_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "items": self.items,
            "attachments": self.attachments,
        }

    class Config:
        from_attributes = True


class SignupSessionListResponse(BaseModel):
    """报名列表响应"""
    items: List[SignupSessionResponse]
    total: int


class SignupApplicationResponse(BaseModel):
    """报名申请响应（包含用户信息，用于审核列表）"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_phone: str
    user_email: Optional[str] = None
    recruitment_session_id: int
    session_name: Optional[str] = None
    self_intro: Optional[str] = None
    status: str
    audit_user_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[SignupItemResponse] = []
    attachments: List[SignupAttachmentResponse] = []

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_phone": self.user_phone,
            "user_email": self.user_email,
            "recruitment_session_id": self.recruitment_session_id,
            "session_name": self.session_name,
            "self_intro": self.self_intro,
            "status": self.status,
            "audit_user_id": self.audit_user_id,
            "audit_time": self.audit_time.isoformat() if self.audit_time else None,
            "audit_reason": self.audit_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "items": self.items,
            "attachments": self.attachments,
        }


class SignupApplicationListResponse(BaseModel):
    """报名申请列表响应（用于审核列表）"""
    items: List[SignupApplicationResponse]
    total: int


class SignupAuditRequest(BaseModel):
    """审核报名请求"""
    status: str = Field(..., description="审核结果：APPROVED / REJECTED")
    reason: Optional[str] = Field(default=None, max_length=255, description="拒绝理由")


class SignupAuditResponse(BaseModel):
    """审核报名响应"""
    detail: str
    signup_id: int
    new_status: str
