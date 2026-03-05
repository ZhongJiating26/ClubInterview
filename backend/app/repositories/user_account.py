from typing import Optional

from sqlmodel import Session, select
import bcrypt

from app.models.user_account import UserAccount
from app.repositories.base import BaseRepository


class UserAccountRepository(BaseRepository[UserAccount]):
    """
    用户账号仓储
    """

    def __init__(self):
        super().__init__(UserAccount)

    # ========= 密码相关 =========

    def hash_password(self, raw_password: str) -> str:
        """
        对密码进行哈希
        bcrypt 限制密码最大 72 字节
        """
        # bcrypt 最大 72 字节，需要截断
        password_bytes = raw_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        """
        验证密码
        """
        password_bytes = raw_password.encode('utf-8')
        # bcrypt hash 存储的是 bytes，需要正确编码
        try:
            return bcrypt.checkpw(password_bytes, password_hash.encode('utf-8'))
        except Exception:
            # 兼容旧格式（已经是 bytes）
            return bcrypt.checkpw(password_bytes, password_hash)

    # ========= 查询 =========

    def get_by_phone(self, session: Session, phone: str) -> Optional[UserAccount]:
        """
        根据手机号查询未删除用户
        """
        stmt = (
            select(UserAccount)
            .where(UserAccount.phone == phone)
            .where(UserAccount.is_deleted == 0)
        )
        return session.execute(stmt).scalar_one_or_none()

    # ========= 创建用户（注册核心） ==========

    def create_user(
        self,
        session: Session,
        *,
        phone: str,
        password: Optional[str] = None,
        name: Optional[str] = None,
        school_id: Optional[int] = None,
    ) -> UserAccount:
        """
        创建新用户（密码可选，用于注册时仅手机号场景）
        """
        password_hash = self.hash_password(password) if password else None

        user = UserAccount(
            phone=phone,
            password_hash=password_hash,
            name=name,
            school_id=school_id,
        )

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    #查询ID

    def get_by_id(self, session: Session, user_id: int) -> Optional[UserAccount]:
        """
        根据 ID 查询未删除用户
        """
        stmt = (
            select(UserAccount)
            .where(UserAccount.id == user_id)
            .where(UserAccount.is_deleted == 0)
        )
        return session.execute(stmt).scalar_one_or_none()

    def init_account(
            self,
            session: Session,
            *,
            user: UserAccount,
            password: str,
            name: str,
            id_card_no: str,
            school_code: str,
            major: str,
            student_no: str,
            email: Optional[str] = None,
            avatar_url: Optional[str] = None,
    ) -> UserAccount:
        """
        账号初始化：设置密码 + 补全资料
        注意：这里不做权限判断（是否允许初始化），权限判断放在 API 层
        """
        user.password_hash = self.hash_password(password)
        user.name = name
        user.id_card_no = id_card_no
        user.school_code = school_code
        user.major = major
        user.student_no = student_no
        user.email = email
        user.avatar_url = avatar_url

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    # ========= 密码管理 =========

    def change_password(
        self,
        session: Session,
        user: UserAccount,
        new_password: str,
    ) -> UserAccount:
        """
        修改密码
        - 更新密码哈希
        - 增加 token_version 使旧 Token 失效
        """
        user.password_hash = self.hash_password(new_password)
        user.token_version += 1  # 使所有旧 Token 失效

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def soft_delete(self, session: Session, user: UserAccount) -> UserAccount:
        """
        软删除账号
        - 设置 is_deleted = 1
        - 设置 deleted_at 为当前时间
        """
        user.is_deleted = 1
        user.deleted_at = self._get_now()

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def _get_now(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.utcnow()
