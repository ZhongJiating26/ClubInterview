from typing import Optional

from sqlmodel import Field

from app.models.base import BaseModel


class SignupAttachment(BaseModel, table=True):
    """
    报名附件表
    """
    __tablename__ = "signup_attachment"

    signup_session_id: int = Field(
        nullable=False,
        description="报名主表ID"
    )

    file_url: str = Field(
        max_length=255,
        description="文件URL"
    )

    file_type: str = Field(
        max_length=20,
        description="类型：PDF / IMG / DOC"
    )

    file_name: str = Field(
        max_length=255,
        description="原始文件名"
    )

    file_size: Optional[int] = Field(
        default=None,
        description="文件大小（字节）"
    )
