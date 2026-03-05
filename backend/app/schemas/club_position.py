from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_serializer


class PositionCreate(BaseModel):
    """创建岗位请求"""
    department_id: Optional[int] = Field(default=None, description="所属部门ID")
    name: str = Field(..., min_length=1, max_length=100, description="岗位名称")
    description: Optional[str] = Field(default=None, description="岗位描述")
    requirement: Optional[str] = Field(default=None, description="任职要求")


class PositionUpdate(BaseModel):
    """更新岗位请求"""
    department_id: Optional[int] = Field(default=None, description="所属部门ID")
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="岗位名称")
    description: Optional[str] = Field(default=None, description="岗位描述")
    requirement: Optional[str] = Field(default=None, description="任职要求")


class PositionResponse(BaseModel):
    """岗位响应"""
    id: int
    club_id: int
    department_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    requirement: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "club_id": self.club_id,
            "department_id": self.department_id,
            "name": self.name,
            "description": self.description,
            "requirement": self.requirement,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    class Config:
        from_attributes = True


class PositionListResponse(BaseModel):
    """岗位列表响应"""
    items: list[PositionResponse]
    total: int
