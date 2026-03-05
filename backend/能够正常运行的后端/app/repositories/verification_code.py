from datetime import datetime
from typing import Optional

from sqlmodel import Session, select, and_

from app.models.verification_code import VerificationCode
from app.repositories.base import BaseRepository


class VerificationCodeRepository(BaseRepository[VerificationCode]):
    """
    验证码仓储
    """

    def __init__(self):
        super().__init__(VerificationCode)

    def get_valid_code(
        self,
        session: Session,
        phone: str,
        code: str,
        scene: str,
    ) -> Optional[VerificationCode]:
        """
        获取有效的验证码（未过期、未使用）
        """
        stmt = (
            select(VerificationCode)
            .where(VerificationCode.phone == phone)
            .where(VerificationCode.code == code)
            .where(VerificationCode.scene == scene)
            .where(VerificationCode.is_used == 0)
            .where(VerificationCode.expired_at > datetime.utcnow())
            .where(VerificationCode.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def mark_as_used(self, session: Session, record: VerificationCode) -> VerificationCode:
        """标记验证码已使用"""
        record.is_used = 1
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def create_code(
        self,
        session: Session,
        phone: str,
        code: str,
        scene: str,
        expired_at: datetime,
    ) -> VerificationCode:
        """
        创建验证码记录
        """
        record = VerificationCode(
            phone=phone,
            scene=scene,
            code=code,
            expired_at=expired_at,
            is_used=0,
        )
        return self.create(session, record)

    def delete_expired_codes(self, session: Session, phone: str, scene: str) -> int:
        """
        删除指定手机号和场景的过期验证码（软删除）
        返回删除数量
        """
        from sqlmodel import update

        # 软删除过期的验证码
        stmt = (
            update(VerificationCode)
            .where(VerificationCode.phone == phone)
            .where(VerificationCode.scene == scene)
            .where(VerificationCode.is_deleted == 0)
            .where(
                (VerificationCode.expired_at < datetime.utcnow()) |
                (VerificationCode.is_used == 1)
            )
            .values(is_deleted=1, deleted_at=datetime.utcnow())
        )
        result = session.execute(stmt)
        session.commit()
        return result.rowcount
