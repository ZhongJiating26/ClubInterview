from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar, List, Any, Dict

from sqlmodel import Session, select
from sqlmodel.sql.expression import Select

from app.models.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """
    通用仓储：默认只操作未删除数据（is_deleted=0）
    """
    def __init__(self, model: Type[ModelT]):
        self.model = model

    # ---------- 查询构造器（方便复用/扩展） ----------
    def _base_stmt(self, include_deleted: bool = False) -> Select:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == 0)
        return stmt

    # ---------- 基础查询 ----------
    def get(self, session: Session, obj_id: int, *, include_deleted: bool = False) -> Optional[ModelT]:
        stmt = self._base_stmt(include_deleted=include_deleted).where(self.model.id == obj_id)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def list(
        self,
        session: Session,
        *,
        include_deleted: bool = False,
        offset: int = 0,
        limit: int = 20,
        order_by: Any = None,
    ) -> List[ModelT]:
        stmt = self._base_stmt(include_deleted=include_deleted)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = session.execute(stmt)
        return list(result.scalars().all())

    # ---------- 创建/更新 ----------
    def create(self, session: Session, obj: ModelT) -> ModelT:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def update(self, session: Session, obj: ModelT, data: Dict[str, Any]) -> ModelT:
        """
        注意：只更新传入字段；并自动 touch updated_at
        """
        for k, v in data.items():
            setattr(obj, k, v)
        obj.touch()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------- 软删除/恢复 ----------
    def soft_delete(self, session: Session, obj: ModelT) -> ModelT:
        obj.soft_delete()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def restore(self, session: Session, obj: ModelT) -> ModelT:
        obj.restore()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
