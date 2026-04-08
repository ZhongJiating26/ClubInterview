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

    # ============ 社团管理增强功能 ============

    def get_club_list(
        self,
        session: Session,
        school_code: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取社团列表（分页、搜索）

        Args:
            session: 数据库会话
            school_code: 学校标识码筛选
            status: 状态筛选
            category: 分类筛选
            keyword: 关键词搜索（社团名称）
            page: 页码
            page_size: 每页数量

        Returns:
            包含 items 和 total 的字典
        """
        # 查询社团，关联学校表
        stmt = (
            select(Club, School)
            .join(School, Club.school_code == School.code)
            .where(Club.is_deleted == 0)
        )

        # 筛选条件
        if school_code:
            stmt = stmt.where(Club.school_code == school_code)
        if status:
            stmt = stmt.where(Club.status == status)
        if category:
            stmt = stmt.where(Club.category == category)
        if keyword:
            stmt = stmt.where(Club.name.contains(keyword))

        # 计算总数
        from sqlmodel import func
        count_stmt = select(func.count()).select_from(stmt)
        total = session.execute(count_stmt).scalar()

        # 分页
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        stmt = stmt.order_by(Club.created_at.desc())

        result = session.execute(stmt)
        rows = result.all()

        # 获取 storage service
        storage = get_storage_service()

        # 组装结果
        items = []
        for club, school in rows:
            items.append({
                "id": club.id,
                "school_name": school.name,
                "name": club.name,
                "logo_url": storage.get_object_url(club.logo_url) if club.logo_url else None,
                "category": club.category,
                "description": club.description,
                "status": club.status,
                "created_at": club.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return {
            "items": items,
            "total": total,
        }

    def audit_club(
        self,
        session: Session,
        club: Club,
        approved: bool,
        reason: Optional[str] = None,
    ) -> Club:
        """
        审核社团

        Args:
            session: 数据库会话
            club: 社团实例
            approved: 是否通过
            reason: 拒绝原因（approved=False 时必填）

        Returns:
            更新后的社团实例
        """
        club.status = "ACTIVE" if approved else "INACTIVE"

        # 如果拒绝，可以将原因存储在 description 中
        if not approved and reason:
            if club.description:
                club.description += f"\n\n审核拒绝原因：{reason}"
            else:
                club.description = f"审核拒绝原因：{reason}"

        return self.update(session, club, {})

    def get_club_members(
        self,
        session: Session,
        club_id: int,
    ) -> dict:
        """
        获取社团成员列表

        Args:
            session: 数据库会话
            club_id: 社团ID

        Returns:
            包含 items 和 total 的字典
        """
        from app.models.user_role import UserRole
        from app.models.user_account import UserAccount
        from app.models.role import Role

        # 查询社团成员
        stmt = (
            select(UserRole, UserAccount, Role)
            .join(UserAccount, UserRole.user_id == UserAccount.id)
            .join(Role, UserRole.role_id == Role.id)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
            .where(UserAccount.is_deleted == 0)
        )

        result = session.execute(stmt)
        rows = result.all()

        # 计算总数
        total = len(rows)

        # 组装结果
        items = []
        for user_role, user, role in rows:
            items.append({
                "user_id": user.id,
                "user_name": user.name,
                "user_phone": user.phone,
                "user_email": user.email,
                "role_id": role.id,
                "role_name": role.name,
                "club_id": club_id,
                "joined_at": user_role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return {
            "items": items,
            "total": total,
        }

    def get_club_stats(
        self,
        session: Session,
        club_id: int,
    ) -> dict:
        """
        获取社团统计数据

        Args:
            session: 数据库会话
            club_id: 社团ID

        Returns:
            统计数据字典
        """
        from app.models.user_role import UserRole
        from app.models.signup_session import SignupSession
        from app.models.interview_candidate import InterviewCandidate
        from sqlmodel import func

        # 总成员数
        members_stmt = (
            select(func.count())
            .select_from(UserRole)
            .where(UserRole.club_id == club_id)
            .where(UserRole.is_deleted == 0)
        )
        total_members = session.execute(members_stmt).scalar() or 0

        # 活跃岗位数（未删除的岗位）
        from app.models.club_position import ClubPosition
        positions_stmt = (
            select(func.count())
            .select_from(ClubPosition)
            .where(ClubPosition.club_id == club_id)
            .where(ClubPosition.is_deleted == 0)
        )
        active_positions = session.execute(positions_stmt).scalar() or 0

        # 活跃招新场次数
        now = datetime.now()
        recruitments_stmt = (
            select(func.count())
            .select_from(RecruitmentSession)
            .where(RecruitmentSession.club_id == club_id)
            .where(RecruitmentSession.is_deleted == 0)
            .where(RecruitmentSession.end_time >= now)
        )
        active_recruitments = session.execute(recruitments_stmt).scalar() or 0

        # 总报名数
        applications_stmt = (
            select(func.count())
            .select_from(SignupSession)
            .join(RecruitmentSession, SignupSession.recruitment_session_id == RecruitmentSession.id)
            .where(RecruitmentSession.club_id == club_id)
            .where(SignupSession.is_deleted == 0)
        )
        total_applications = session.execute(applications_stmt).scalar() or 0

        # 待审核报名数
        pending_stmt = (
            select(func.count())
            .select_from(SignupSession)
            .join(RecruitmentSession, SignupSession.recruitment_session_id == RecruitmentSession.id)
            .where(RecruitmentSession.club_id == club_id)
            .where(SignupSession.is_deleted == 0)
            .where(SignupSession.status == "PENDING")
        )
        pending_reviews = session.execute(pending_stmt).scalar() or 0

        # 总面试数
        interviews_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .join(RecruitmentSession, InterviewCandidate.recruitment_session_id == RecruitmentSession.id)
            .where(RecruitmentSession.club_id == club_id)
            .where(InterviewCandidate.is_deleted == 0)
        )
        total_interviews = session.execute(interviews_stmt).scalar() or 0

        # 即将到来的面试数（未来7天）
        from datetime import timedelta
        upcoming_start = now
        upcoming_end = now + timedelta(days=7)

        upcoming_stmt = (
            select(func.count())
            .select_from(InterviewCandidate)
            .join(RecruitmentSession, InterviewCandidate.recruitment_session_id == RecruitmentSession.id)
            .where(RecruitmentSession.club_id == club_id)
            .where(InterviewCandidate.is_deleted == 0)
            .where(InterviewCandidate.planned_start_time >= upcoming_start)
            .where(InterviewCandidate.planned_start_time <= upcoming_end)
        )
        upcoming_interviews = session.execute(upcoming_stmt).scalar() or 0

        return {
            "club_id": club_id,
            "club_name": self.get(session, club_id).name,
            "total_members": total_members,
            "active_positions": active_positions,
            "active_recruitments": active_recruitments,
            "total_applications": total_applications,
            "total_interviews": total_interviews,
            "pending_reviews": pending_reviews,
            "upcoming_interviews": upcoming_interviews,
        }
