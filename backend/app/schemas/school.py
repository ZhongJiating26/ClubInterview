from typing import List
from pydantic import BaseModel, Field


class SchoolItem(BaseModel):
    """学校搜索结果项"""
    id: int
    name: str
    code: str | None = None


class SchoolSearchResponse(BaseModel):
    """学校搜索响应"""
    total: int
    items: List[SchoolItem]
