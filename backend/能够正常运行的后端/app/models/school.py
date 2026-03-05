from typing import Optional

from sqlmodel import Field

from app.models.base import BaseModel


class School(BaseModel, table=True):
    """
    学校表：基础维度表
    """
    __tablename__ = "school"

    name: str = Field(max_length=100, nullable=False, description="学校名称")
    code: Optional[str] = Field(default=None, max_length=50, description="学校标识码")
