from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, model_serializer


class RecruitmentSessionPositionCreate(BaseModel):
    """关联岗位请求"""
    position_id: int = Field(..., description="岗位ID")
    recruit_quota: Optional[int] = Field(default=None, ge=1, description="招新人次")


class RecruitmentSessionCreate(BaseModel):
    """创建招新场次请求"""
    name: str = Field(..., min_length=1, max_length=100, description="招新场次名称")
    description: Optional[str] = Field(default=None, description="招新说明")
    start_time: datetime = Field(..., description="报名开始时间")
    end_time: datetime = Field(..., description="报名截止时间")
    max_candidates: Optional[int] = Field(default=None, ge=1, description="报名上限人数")
    status: Literal["DRAFT", "PUBLISHED"] = Field(default="DRAFT", description="创建后的场次状态")
    positions: List["RecruitmentSessionPositionCreate"] = Field(default_factory=list, description="场次关联岗位")


class RecruitmentSessionUpdate(BaseModel):
    """更新招新场次请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="招新场次名称")
    description: Optional[str] = Field(default=None, description="招新说明")
    start_time: Optional[datetime] = Field(default=None, description="报名开始时间")
    end_time: Optional[datetime] = Field(default=None, description="报名截止时间")
    max_candidates: Optional[int] = Field(default=None, ge=1, description="报名上限人数")
    status: Optional[str] = Field(default=None, description="状态：DRAFT / PUBLISHED / CLOSED")


class RecruitmentSessionPositionUpdate(BaseModel):
    """更新岗位配额请求"""
    recruit_quota: Optional[int] = Field(default=None, ge=1, description="招新人次")


class RecruitmentSessionPositionResponse(BaseModel):
    """招新岗位响应"""
    id: int
    session_id: int
    position_id: int
    position_name: str
    position_description: Optional[str] = None
    position_requirement: Optional[str] = None
    recruit_quota: Optional[int] = None

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "position_id": self.position_id,
            "position_name": self.position_name,
            "position_description": self.position_description,
            "position_requirement": self.position_requirement,
            "recruit_quota": self.recruit_quota,
        }


class RecruitmentSessionResponse(BaseModel):
    """招新场次响应"""
    id: int
    club_id: int
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    max_candidates: Optional[int] = None
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    positions: List[RecruitmentSessionPositionResponse] = []

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "club_id": self.club_id,
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "max_candidates": self.max_candidates,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "positions": self.positions,
        }

    class Config:
        from_attributes = True


class RecruitmentSessionListResponse(BaseModel):
    """招新场次列表响应"""
    items: List[RecruitmentSessionResponse]
    total: int
