from pydantic import BaseModel


class DashboardDailyApplications(BaseModel):
    date: str
    count: int


class DashboardDepartmentStats(BaseModel):
    department_name: str
    application_count: int
    admission_count: int


class DashboardPositionStats(BaseModel):
    position_name: str
    department_name: str
    application_count: int
    admission_count: int


class DashboardStatsResponse(BaseModel):
    total_sessions: int
    active_sessions: int
    total_applications: int
    pending_review: int
    total_interviews: int
    completed_interviews: int
    admitted_count: int
    application_growth: float
    interview_completion_rate: float
    admission_rate: float
    daily_applications: list[DashboardDailyApplications]
    department_stats: list[DashboardDepartmentStats]
    position_stats: list[DashboardPositionStats]
