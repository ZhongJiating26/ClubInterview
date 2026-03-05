from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_serializer


class DepartmentCreate(BaseModel):
    """创建部门请求"""
    name: str = Field(..., min_length=1, max_length=100, description="部门名称")
    description: Optional[str] = Field(default=None, description="部门描述")


class DepartmentUpdate(BaseModel):
    """更新部门请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="部门名称")
    description: Optional[str] = Field(default=None, description="部门描述")


class DepartmentResponse(BaseModel):
    """部门响应"""
    id: int
    club_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": self.id,
            "club_id": self.club_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    """部门列表响应"""
    items: list[DepartmentResponse]
    total: int
