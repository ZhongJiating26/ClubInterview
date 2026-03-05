import { get, post, put, del } from '../request'

// 报名状态
export type SignupStatus = 'PENDING' | 'APPROVED' | 'REJECTED'

// 报名的岗位项
export interface SignupItem {
  id: number
  signup_session_id: number
  department_id: number | null
  position_id: number
  department_name?: string
  position_name?: string
}

// 报名信息
export interface SignupApplication {
  id: number
  user_id: number
  recruitment_session_id: number
  self_intro: string | null
  status: SignupStatus
  audit_user_id: number | null
  audit_time: string | null
  audit_reason: string | null
  created_at: string
  updated_at: string
  items: SignupItem[]
  attachments: any[]
  // 额外字段（可能由后端返回）
  user_name?: string
  user_phone?: string
  user_email?: string
  session_name?: string
}

// 报名列表响应
export interface SignupListResponse {
  items: SignupApplication[]
  total: number
}

// 审核报名请求
export interface AuditSignupData {
  status: 'APPROVED' | 'REJECTED'
  reason?: string
}

// 获取报名审核列表参数
export interface SignupListParams {
  recruitment_session_id: number
  status?: SignupStatus
  page?: number
  page_size?: number
}

// ==================== 学生报名 ====================

// 提交报名请求
export interface SubmitSignupData {
  recruitment_session_id: number
  position_ids: number[]
  self_intro?: string
}

// 提交报名
export function submitSignup(data: SubmitSignupData) {
  return post<{ signup_id: number; status: string }>('/api/student/signup/applications', data)
}

// 获取用户的报名列表
export interface MySignupParams {
  recruitment_session_id?: number
  status?: SignupStatus
  page?: number
  page_size?: number
}

export function getMySignups(params?: MySignupParams) {
  return get<SignupListResponse>('/api/student/signup/applications', params)
}

// ==================== 报名审核（社团管理员） ====================

// 获取报名审核列表
export function getSignupApplications(params: SignupListParams) {
  return get<SignupListResponse>('/api/admin/signup/applications', params)
}

// 获取报名详情
export function getSignupApplicationDetail(id: number) {
  return get<SignupApplication>(`/api/admin/signup/applications/${id}`)
}

// 审核报名
export function auditSignupApplication(id: number, data: AuditSignupData) {
  return post<{ detail: string; signup_id: number; new_status: string }>(
    `/api/admin/signup/applications/${id}/audit`,
    data
  )
}

// ==================== 报名查看（面试官） ====================

// 获取报名列表（面试官）
export function getInterviewerSignupApplications(params: SignupListParams) {
  return get<SignupListResponse>('/api/interviewer/signup/applications', params)
}

// 获取报名详情（面试官）
export function getInterviewerSignupApplicationDetail(id: number) {
  return get<SignupApplication>(`/api/interviewer/signup/applications/${id}`)
}
