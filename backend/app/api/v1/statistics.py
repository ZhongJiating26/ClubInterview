from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.admission_result import AdmissionResult
from app.models.club_position import ClubPosition
from app.models.department import Department
from app.models.interview_candidate import InterviewCandidate
from app.models.interview_session import InterviewSession
from app.models.recruitment_session import RecruitmentSession
from app.models.role import Role
from app.models.signup_item import SignupItem
from app.models.signup_session import SignupSession
from app.models.user_account import UserAccount
from app.models.user_role import UserRole
from app.schemas.statistics import (
    DashboardDailyApplications,
    DashboardDepartmentStats,
    DashboardPositionStats,
    DashboardStatsResponse,
)


router = APIRouter(tags=["统计"])


def _ensure_club_admin(session: Session, current_user: UserAccount, club_id: int) -> None:
    club_admin_role = session.execute(
        select(Role)
        .where(Role.code == "CLUB_ADMIN")
        .where(Role.is_deleted == 0)
    ).scalar_one_or_none()

    if not club_admin_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统角色配置错误",
        )

    relation = session.execute(
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .where(UserRole.role_id == club_admin_role.id)
        .where(UserRole.club_id == club_id)
        .where(UserRole.is_deleted == 0)
    ).scalar_one_or_none()

    if not relation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看该社团的数据看板",
        )


def _round_percent(value: float) -> float:
    return round(value, 1)


@router.get("/admin/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    club_id: int,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _ensure_club_admin(session, current_user, club_id)

    now = datetime.utcnow()
    today = now.date()
    seven_days_ago = today - timedelta(days=6)
    previous_period_start = seven_days_ago - timedelta(days=7)
    previous_period_end = seven_days_ago - timedelta(days=1)

    recruitment_sessions = session.execute(
        select(RecruitmentSession)
        .where(RecruitmentSession.club_id == club_id)
        .where(RecruitmentSession.is_deleted == 0)
    ).scalars().all()

    recruitment_ids = [item.id for item in recruitment_sessions]

    if not recruitment_ids:
        return DashboardStatsResponse(
            total_sessions=0,
            active_sessions=0,
            total_applications=0,
            pending_review=0,
            total_interviews=0,
            completed_interviews=0,
            admitted_count=0,
            application_growth=0.0,
            interview_completion_rate=0.0,
            admission_rate=0.0,
            daily_applications=[
                DashboardDailyApplications(
                    date=(seven_days_ago + timedelta(days=offset)).isoformat(),
                    count=0,
                )
                for offset in range(7)
            ],
            department_stats=[],
            position_stats=[],
        )

    signup_sessions = session.execute(
        select(SignupSession)
        .where(SignupSession.recruitment_session_id.in_(recruitment_ids))
        .where(SignupSession.is_deleted == 0)
    ).scalars().all()

    signup_ids = [item.id for item in signup_sessions]
    signups_by_id = {item.id: item for item in signup_sessions}

    interview_sessions = session.execute(
        select(InterviewSession)
        .where(InterviewSession.club_id == club_id)
        .where(InterviewSession.is_deleted == 0)
    ).scalars().all()
    interview_session_ids = [item.id for item in interview_sessions]

    interview_candidates = []
    if interview_session_ids:
        interview_candidates = session.execute(
            select(InterviewCandidate)
            .where(InterviewCandidate.session_id.in_(interview_session_ids))
            .where(InterviewCandidate.is_deleted == 0)
        ).scalars().all()

    admission_results = []
    if signup_ids:
        admission_results = session.execute(
            select(AdmissionResult)
            .where(AdmissionResult.signup_session_id.in_(signup_ids))
            .where(AdmissionResult.is_deleted == 0)
        ).scalars().all()

    signup_items = []
    if signup_ids:
        signup_items = session.execute(
            select(SignupItem)
            .where(SignupItem.signup_session_id.in_(signup_ids))
            .where(SignupItem.is_deleted == 0)
        ).scalars().all()

    position_ids = sorted({item.position_id for item in signup_items if item.position_id})
    department_ids = sorted({item.department_id for item in signup_items if item.department_id})

    positions = {}
    if position_ids:
        positions = {
            item.id: item
            for item in session.execute(
                select(ClubPosition)
                .where(ClubPosition.id.in_(position_ids))
                .where(ClubPosition.is_deleted == 0)
            ).scalars().all()
        }

    departments = {}
    if department_ids:
        departments = {
            item.id: item
            for item in session.execute(
                select(Department)
                .where(Department.id.in_(department_ids))
                .where(Department.is_deleted == 0)
            ).scalars().all()
        }

    total_sessions = len(recruitment_sessions)
    active_sessions = sum(
        1
        for item in recruitment_sessions
        if item.status == "PUBLISHED" and item.start_time <= now <= item.end_time
    )

    total_applications = len(signup_sessions)
    pending_review = sum(1 for item in signup_sessions if item.status == "PENDING")
    total_interviews = len(interview_candidates)
    completed_interviews = sum(1 for item in interview_candidates if item.status == "COMPLETED")
    admitted_count = sum(1 for item in admission_results if item.result == "PASS")

    interview_completion_rate = _round_percent(
        (completed_interviews / total_interviews * 100) if total_interviews else 0.0
    )
    admission_rate = _round_percent(
        (admitted_count / completed_interviews * 100) if completed_interviews else 0.0
    )

    current_period_count = sum(
        1 for item in signup_sessions if seven_days_ago <= item.created_at.date() <= today
    )
    previous_period_count = sum(
        1
        for item in signup_sessions
        if previous_period_start <= item.created_at.date() <= previous_period_end
    )
    if previous_period_count == 0:
        application_growth = 100.0 if current_period_count > 0 else 0.0
    else:
        application_growth = _round_percent(
            (current_period_count - previous_period_count) / previous_period_count * 100
        )

    daily_counter: dict[str, int] = {
        (seven_days_ago + timedelta(days=offset)).isoformat(): 0 for offset in range(7)
    }
    for item in signup_sessions:
        created_day = item.created_at.date()
        if seven_days_ago <= created_day <= today:
            day_key = created_day.isoformat()
            daily_counter[day_key] += 1

    daily_applications = [
        DashboardDailyApplications(date=day_key, count=daily_counter[day_key])
        for day_key in sorted(daily_counter.keys())
    ]

    admitted_signup_ids = {
        item.signup_session_id
        for item in admission_results
        if item.result == "PASS" and item.signup_session_id is not None
    }

    department_application_counts: dict[int | None, int] = defaultdict(int)
    department_admission_counts: dict[int | None, int] = defaultdict(int)
    position_application_counts: dict[int, int] = defaultdict(int)
    position_admission_counts: dict[int, int] = defaultdict(int)

    for item in signup_items:
        department_application_counts[item.department_id] += 1
        position_application_counts[item.position_id] += 1

        if item.signup_session_id in admitted_signup_ids:
            department_admission_counts[item.department_id] += 1
            position_admission_counts[item.position_id] += 1

    department_stats = [
        DashboardDepartmentStats(
            department_name=departments[department_id].name if department_id in departments else "未分配部门",
            application_count=application_count,
            admission_count=department_admission_counts.get(department_id, 0),
        )
        for department_id, application_count in sorted(
            department_application_counts.items(),
            key=lambda pair: (-pair[1], 0 if pair[0] is None else pair[0]),
        )
    ]

    position_stats = [
        DashboardPositionStats(
            position_name=positions[position_id].name if position_id in positions else f"岗位{position_id}",
            department_name=(
                departments.get(positions[position_id].department_id).name
                if position_id in positions and positions[position_id].department_id in departments
                else "未分配部门"
            ),
            application_count=application_count,
            admission_count=position_admission_counts.get(position_id, 0),
        )
        for position_id, application_count in sorted(
            position_application_counts.items(),
            key=lambda pair: (-pair[1], pair[0]),
        )
    ]

    return DashboardStatsResponse(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        total_applications=total_applications,
        pending_review=pending_review,
        total_interviews=total_interviews,
        completed_interviews=completed_interviews,
        admitted_count=admitted_count,
        application_growth=application_growth,
        interview_completion_rate=interview_completion_rate,
        admission_rate=admission_rate,
        daily_applications=daily_applications,
        department_stats=department_stats,
        position_stats=position_stats,
    )
