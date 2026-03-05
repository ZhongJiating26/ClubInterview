from typing import Optional

from sqlmodel import Field

from app.models.base import BaseModel


class SignupItem(BaseModel, table=True):
    """
    报名子表（一个学生在本次招新报的岗位）
    """
    __tablename__ = "signup_item"

    signup_session_id: int = Field(
        nullable=False,
        description="报名主表ID"
    )

    department_id: Optional[int] = Field(
        default=None,
        description="部门ID"
    )

    position_id: int = Field(
        nullable=False,
        description="岗位ID"
    )
