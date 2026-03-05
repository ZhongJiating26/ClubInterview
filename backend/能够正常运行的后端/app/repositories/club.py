from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select

from app.models.club import Club
from app.models.school import School
from app.models.recruitment_session import RecruitmentSession
from app.repositories.base import BaseRepository
from app.core.storage import get_storage_service


class ClubRepository(BaseRepository[Club]):
    """
    社团仓储
    """

    def __init__(self):
        super().__init__(Club)

    def get_by_school_code(
        self,
        session: Session,
        school_code: str,
    ) -> List[Club]:
        """
        获取学校的所有社团
        """
        stmt = (
            select(Club)
            .where(Club.school_code == school_code)
            .where(Club.status == "ACTIVE")
            .where(Club.is_deleted == 0)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_name_and_school(
        self,
        session: Session,
        name: str,
        school_code: str,
    ) -> Optional[Club]:
        """
        根据名称和学校查找社团
        """
        stmt = (
            select(Club)
            .where(Club.name == name)
            .where(Club.school_code == school_code)
            .where(Club.is_deleted == 0)
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_or_create(
        self,
        session: Session,
        name: str,
        school_code: str,
    ) -> tuple[Club, bool]:
        """
        获取或创建社团
        返回：(社团实例, 是否为新创建)
        """
        # 尝试查找
        existing = self.get_by_name_and_school(session, name, school_code)
        if existing:
            return existing, False

        # 创建新社团
        club = Club(
            name=name,
            school_code=school_code,
            logo_url="dev/clubs/logos/club-logo-default.png",
            status="REVIEW",  # 新社团需要审核
        )
        return self.create(session, club), True

    def update_info(
        self,
        session: Session,
        club: Club,
        *,
        logo_url: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        cert_file_url: Optional[str] = None,
    ) -> Club:
        """
        完善/修改社团信息
        """
        if logo_url is not None:
            club.logo_url = logo_url
        if category is not None:
            club.category = category
        if description is not None:
            club.description = description
        if cert_file_url is not None:
            club.cert_file_url = cert_file_url

        return self.update(session, club, {})

    def get_for_home(
        self,
        session: Session,
        school_code: str,
        status: Optional[str] = None,
    ) -> List[dict]:
        """
        获取首页社团列表（含学校名称和招新状态）

        Args:
            session: 数据库会话
            school_code: 学校编码
            status: 社团状态筛选（如 "APPROVED"）

        Returns:
            包含社团信息和招新状态的字典列表
        """
        # 查询社团，关联学校表获取学校名称
        stmt = (
            select(Club, School)
            .join(School, Club.school_code == School.code)
            .where(Club.school_code == school_code)
            .where(Club.is_deleted == 0)
        )

        if status:
            stmt = stmt.where(Club.status == status)

        stmt = stmt.order_by(Club.created_at.desc())
        result = session.execute(stmt)
        rows = result.all()

        # 获取当前时间
        now = datetime.now()

        # 获取该学校所有社团的ID
        club_ids = [row[0].id for row in rows]

        # 查询正在招新的场次（只查询已发布的场次）
        recruiting_stmt = (
            select(RecruitmentSession.club_id)
            .where(RecruitmentSession.club_id.in_(club_ids))
            .where(RecruitmentSession.is_deleted == 0)
            .where(RecruitmentSession.status == "PUBLISHED")
            .where(RecruitmentSession.start_time <= now)
            .where(RecruitmentSession.end_time >= now)
            .distinct()
        )
        recruiting_result = session.execute(recruiting_stmt)
        recruiting_club_ids = set(r[0] for r in recruiting_result.all())

        # 获取 storage service 用于转换 URL
        storage = get_storage_service()

        # 组装结果
        clubs_data = []
        for club, school in rows:
            clubs_data.append({
                "id": club.id,
                "name": club.name,
                "logo_url": storage.get_object_url(club.logo_url) if club.logo_url else None,
                "description": club.description,
                "category": club.category,
                "school_name": school.name,
                "status": club.status,
                "recruiting_status": "RECRUITING" if club.id in recruiting_club_ids else "NO_RECRUITMENT",
            })

        return clubs_data
