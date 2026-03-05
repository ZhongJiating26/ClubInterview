from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class Club(BaseModel, table=True):
    """
    社团表
    """
    __tablename__ = "club"

    school_code: str = Field(
        max_length=50,
        nullable=False,
        description="所属学校标识码"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="社团名称"
    )

    logo_url: Optional[str] = Field(
        default="clubs/logos/club-logo-default.png",
        max_length=255,
        description="LOGO 存储路径"
    )

    category: Optional[str] = Field(
        default=None,
        max_length=50,
        description="分类（技术/文艺等）"
    )

    description: Optional[str] = Field(
        default=None,
        description="社团介绍"
    )

    cert_file_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="认证材料 URL"
    )

    status: str = Field(
        max_length=20,
        default="REVIEW",
        description="状态：ACTIVE / INACTIVE / REVIEW"
    )
