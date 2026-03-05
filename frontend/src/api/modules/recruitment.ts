import { get, post, put, del } from '../request'

// 招新场次状态
export type SessionStatus = 'DRAFT' | 'PUBLISHED' | 'CLOSED'

// 招新场次关联的岗位
export interface SessionPosition {
  id: number
  session_id: number
  position_id: number
  position_name: string
  position_description: string | null
  position_requirement: string | null
  recruit_quota: number
}

// 招新场次
export interface RecruitmentSession {
  id: number
  club_id: number
  name: string
  description: string | null
  start_time: string
  end_time: string
  max_candidates: number
  status: SessionStatus
  created_by: number
  created_at: string
  updated_at: string
  positions?: SessionPosition[]
}

// 关联岗位到招新场次的请求
export interface AddSessionPositionData {
  position_id: number
  recruit_quota: number
}

// 创建招新场次请求（不包含 club_id，club_id 通过 query 参数传递）
export interface CreateSessionData {
  name: string
  description?: string
  start_time: string
  end_time: string
  max_candidates?: number
}

// 创建招新场次（club_id 作为 query 参数）
export function createRecruitmentSession(clubId: number, data: CreateSessionData) {
  return post<RecruitmentSession>('/api/recruitment/sessions', data, {
    params: { club_id: clubId }
  })
}

// 更新招新场次请求
export interface UpdateSessionData {
  name?: string
  description?: string
  start_time?: string
  end_time?: string
  max_candidates?: number
  status?: SessionStatus
}

// ==================== 招新场次管理 ====================

// 获取招新场次列表
export function getRecruitmentSessions(params?: {
  club_id?: number
  status?: SessionStatus
}) {
  return get<RecruitmentSession[]>('/api/recruitment/sessions', params)
}

// 获取招新场次详情
export function getRecruitmentSession(id: number) {
  return get<RecruitmentSession>(`/api/recruitment/sessions/${id}`)
}

// 更新招新场次
export function updateRecruitmentSession(id: number, data: UpdateSessionData) {
  return put<RecruitmentSession>(`/api/recruitment/sessions/${id}`, data)
}

// 删除招新场次
export function deleteRecruitmentSession(id: number) {
  return del(`/api/recruitment/sessions/${id}`)
}

// ==================== 招新场次岗位关联 ====================

// 关联岗位到招新场次
export function addSessionPosition(sessionId: number, data: AddSessionPositionData) {
  return post<SessionPosition>(`/api/recruitment/sessions/${sessionId}/positions`, data)
}

// 更新招新场次的岗位配额
export interface UpdateSessionPositionData {
  recruit_quota: number
}

export function updateSessionPosition(sessionId: number, positionId: number, data: UpdateSessionPositionData) {
  return put<SessionPosition>(`/api/recruitment/sessions/${sessionId}/positions/${positionId}`, data)
}

// 取消关联岗位
export function removeSessionPosition(sessionId: number, positionId: number) {
  return del(`/api/recruitment/sessions/${sessionId}/positions/${positionId}`)
}

// 获取招新场次关联的岗位
export function getSessionPositions(sessionId: number) {
  return get<SessionPosition[]>(`/api/recruitment/sessions/${sessionId}/positions`)
}
