from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


def utcnow() -> datetime:
    # 统一用 UTC，避免服务器时区/本地时区混乱
    return datetime.utcnow()


class BaseModel(SQLModel):
    """
    所有业务表的公共字段（按你文档的软删除规范）
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

    is_deleted: int = Field(default=0, nullable=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    def touch(self) -> None:
        """更新 updated_at（用于更新前手动调用）"""
        self.updated_at = utcnow()

    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = 1
        self.deleted_at = utcnow()
        self.touch()

    def restore(self) -> None:
        """恢复"""
        self.is_deleted = 0
        self.deleted_at = None
        self.touch()
