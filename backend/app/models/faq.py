from typing import Optional
from sqlmodel import Field, Text

from app.models.base import BaseModel


class FAQ(BaseModel, table=True):
    """
    常见问题表
    """
    __tablename__ = "faq"

    club_id: Optional[int] = Field(
        default=None,
        description="关联社团ID（为空表示平台级FAQ）"
    )

    category: str = Field(
        max_length=50,
        nullable=False,
        description="分类"
    )

    question: str = Field(
        max_length=255,
        nullable=False,
        description="问题"
    )

    answer: str = Field(
        nullable=False,
        max_length=2000,
        description="答案"
    )

    order_no: int = Field(
        nullable=False,
        description="排序"
    )

    is_pinned: bool = Field(
        nullable=False,
        default=False,
        description="是否置顶"
    )
