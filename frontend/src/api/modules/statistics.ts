import { get } from '../request'
import { post } from '../request'

export interface StatisticsData {
  totalApplications: number
  pendingApplications: number
  approvedApplications: number
  rejectedApplications: number
  totalInterviews: number
  completedInterviews: number
  upcomingInterviews: number
}

export interface DepartmentStatistics {
  department: string
  total: number
  approved: number
  rejected: number
  pending: number
}

export interface DailyStatistics {
  date: string
  applications: number
  interviews: number
}

export interface DashboardStats {
  total_sessions: number
  active_sessions: number
  total_applications: number
  pending_review: number
  total_interviews: number
  completed_interviews: number
  admitted_count: number
  application_growth: number
  interview_completion_rate: number
  admission_rate: number
  daily_applications: {
    date: string
    count: number
  }[]
  department_stats: {
    department_name: string
    application_count: number
    admission_count: number
  }[]
  position_stats: {
    position_name: string
    department_name: string
    application_count: number
    admission_count: number
  }[]
}

export function getOverviewStatistics() {
  return get('/api/statistics/overview')
}

export function getDashboardStats(clubId: number) {
  return get<DashboardStats>('/api/admin/dashboard', { club_id: clubId })
}

export function getDepartmentStatistics(department?: string) {
  return get('/api/statistics/department', { department })
}

export function getDailyStatistics(params: { startDate: string; endDate: string; type?: string }) {
  return get('/api/statistics/daily', params)
}

export function getInterviewStatistics(interviewId?: number) {
  return get('/api/statistics/interview', { interviewId })
}

export function exportStatistics(params: any) {
  return post('/api/statistics/export', params, { responseType: 'blob' })
}
