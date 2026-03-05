from typing import Optional
from sqlmodel import Field

from app.models.base import BaseModel


class ScoreItem(BaseModel, table=True):
    """
    评分项表
    """
    __tablename__ = "score_item"

    template_id: Optional[int] = Field(
        default=None,
        description="模板ID"
    )

    session_id: Optional[int] = Field(
        default=None,
        description="场次ID（可选，用于场次自定义评分项）"
    )

    name: str = Field(
        max_length=100,
        nullable=False,
        description="评分项名称"
    )

    weight: int = Field(
        nullable=False,
        description="权重"
    )

    max_score: float = Field(
        nullable=False,
        description="满分"
    )

    order_no: int = Field(
        nullable=False,
        description="排序"
    )
