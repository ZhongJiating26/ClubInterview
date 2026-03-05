import { get, post, put, del } from '../request'
import type { SignupApplication } from './application'

// ==================== 类型定义 ====================

// 面试场次状态
export type InterviewSessionStatus = 'DRAFT' | 'OPEN' | 'CLOSED'

// 面试场次
export interface InterviewSession {
  id: number
  club_id: number
  recruitment_session_id: number | null
  name: string
  description: string | null
  start_time: string
  end_time: string
  place: string | null
  status: InterviewSessionStatus
  created_by: number
  created_at: string
  updated_at: string
  // 统计信息（可能在详情接口中返回）
  interviewer_count?: number
  candidate_count?: number
}

// 创建面试场次请求
export interface CreateInterviewSessionData {
  recruitment_session_id?: number
  name: string
  description?: string
  start_time: string
  end_time: string
  place?: string
  status?: InterviewSessionStatus // 添加状态字段
}

// 更新面试场次请求
export interface UpdateInterviewSessionData {
  name?: string
  description?: string
  start_time?: string
  end_time?: string
  place?: string
  status?: InterviewSessionStatus
}

// 面试官
export interface Interviewer {
  id: number
  user_id: number
  club_id: number
  name: string
  phone?: string
  email?: string
}

// 可分配的面试官（包含社团的面试官和管理员）
export interface AssignableInterviewer {
  id: number
  user_id: number
  name: string
  phone?: string
  email?: string
  role: 'CLUB_ADMIN' | 'INTERVIEWER' // 角色：社团管理员或面试官
}

// 分配单个面试官请求
export interface AssignInterviewerData {
  interviewer_id: number
}

// 面试候选人排期
export interface InterviewCandidate {
  id: number
  session_id: number
  signup_application_id: number
  user_id: number
  user_name: string
  user_phone?: string
  position_id: number
  position_name?: string
  department_id?: number
  department_name?: string
  planned_start_time: string
  planned_end_time: string
  actual_start_time: string | null
  actual_end_time: string | null
  status: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
  final_score: number | null
  created_at: string
}

// 生成候选人排期请求
export interface GenerateCandidatesData {
  signup_application_ids?: number[] // 指定要安排的报名ID列表，不传则自动从已通过的报名中生成
  time_slot_duration?: number // 每个时间槽的时长（分钟），默认60
  start_time?: string // 开始时间，默认使用场次开始时间
  end_time?: string // 结束时间，默认使用场次结束时间
}

// 评分模板
export interface ScoreTemplate {
  id: number
  club_id: number
  name: string
  description?: string
  is_default: boolean
  created_at: string
  updated_at: string
}

// 评分项
export interface ScoreItem {
  id: number
  template_id: number | null
  session_id: number | null
  title: string
  description?: string
  max_score: number
  weight: number
  sort_order: number
}

// 设置评分模板请求
export interface SetScoreTemplateData {
  template_id?: number // 使用已有模板
  custom_items?: {
    title: string
    description?: string
    max_score: number
    weight: number
  }[] // 自定义评分项
}

// 面试记录
export interface InterviewRecord {
  id: number
  candidate_id: number
  interviewer_id: number
  recording_url?: string
  transcript?: string
  notes?: string
  total_score?: number
  status: 'PENDING' | 'SCORED'
  created_at: string
  updated_at: string
}

// 面试评分明细
export interface InterviewScore {
  id: number
  record_id: number
  score_item_id: number
  score: number
  notes?: string
}

// 提交评分请求
export interface SubmitScoreData {
  scores: {
    score_item_id: number
    score: number
    notes?: string
  }[]
  notes?: string
}

// 面试结果汇总
export interface InterviewResult {
  candidate_id: number
  user_name: string
  user_phone?: string
  position_name?: string
  department_name?: string
  records: {
    record_id: number
    interviewer_name: string
    total_score: number
    notes?: string
  }[]
  average_score: number
  final_score: number
}

// ==================== 面试场次管理 ====================

// 获取面试场次列表
export function getInterviewSessions(params?: {
  club_id?: number
  recruitment_session_id?: number
  status?: InterviewSessionStatus
}) {
  return get<InterviewSession[]>('/api/interview/sessions', params)
}

// 获取面试场次详情
export function getInterviewSession(id: number) {
  return get<InterviewSession>(`/api/interview/sessions/${id}`)
}

// 创建面试场次
export function createInterviewSession(clubId: number, data: CreateInterviewSessionData) {
  return post<InterviewSession>('/api/interview/sessions', data, {
    params: { club_id: clubId }
  })
}

// 更新面试场次
export function updateInterviewSession(id: number, data: UpdateInterviewSessionData) {
  return put<InterviewSession>(`/api/interview/sessions/${id}`, data)
}

// 删除面试场次
export function deleteInterviewSession(id: number) {
  return del(`/api/interview/sessions/${id}`)
}

// ==================== 面试官分配 ====================

// 获取社团可分配的面试官列表（包含社团的面试官和管理员）
export function getAssignableInterviewers(clubId: number) {
  return get<AssignableInterviewer[]>(`/api/interview/clubs/${clubId}/assignable-interviewers`)
}

// 为场次分配单个面试官
export function assignInterviewer(sessionId: number, data: AssignInterviewerData) {
  return post(`/api/interview/sessions/${sessionId}/interviewers`, data)
}

// 获取场次的面试官列表
export function getSessionInterviewers(sessionId: number) {
  return get<Interviewer[]>(`/api/interview/sessions/${sessionId}/interviewers`)
}

// ==================== 候选人管理 ====================

// 生成候选人排期
export function generateCandidates(sessionId: number, data: GenerateCandidatesData = {}) {
  return post<InterviewCandidate[]>(`/api/interview/sessions/${sessionId}/generate-candidates`, data)
}

// 获取场次的候选人列表
export function getSessionCandidates(sessionId: number, params?: {
  status?: InterviewCandidate['status']
}) {
  return get<InterviewCandidate[]>(`/api/interview/sessions/${sessionId}/candidates`, params)
}

// 获取候选人详情
export function getCandidateDetail(candidateId: number) {
  return get<InterviewCandidate & { application?: any }>(`/api/interview/candidates/${candidateId}`)
}

// ==================== 评分模板 ====================

// 获取评分模板列表
export function getScoreTemplates(params?: { club_id?: number }) {
  return get<ScoreTemplate[]>('/api/score-templates', params)
}

// 获取评分模板的评分项
export function getScoreTemplateItems(templateId: number) {
  return get<ScoreItem[]>(`/api/score-templates/${templateId}/items`)
}

// 获取场次的评分项
export function getSessionScoreItems(sessionId: number) {
  return get<ScoreItem[]>(`/api/interview/sessions/${sessionId}/score-items`)
}

// 设置场次评分模板
export function setScoreTemplate(sessionId: number, data: SetScoreTemplateData) {
  return post<ScoreItem[]>(`/api/interview/sessions/${sessionId}/score-template`, data)
}

// ==================== 面试记录与评分 ====================

// 获取面试记录
export function getInterviewRecord(recordId: number) {
  return get<InterviewRecord & { scores?: InterviewScore[] }>(`/api/interview/records/${recordId}`)
}

// 创建面试记录（面试官点击开始面试）
export function startInterview(candidateId: number) {
  return post<InterviewRecord>(`/api/interview/records/${candidateId}/start`)
}

// 更新面试记录文本
export function updateInterviewRecord(recordId: number, data: {
  notes?: string
  transcript?: string
}) {
  return put<InterviewRecord>(`/api/interview/records/${recordId}`, data)
}

// 提交评分
export function submitScore(recordId: number, data: SubmitScoreData) {
  return post<InterviewRecord>(`/api/interview/records/${recordId}/score`, data)
}

// 修改评分
export function resubmitScore(recordId: number, data: SubmitScoreData) {
  return post<InterviewRecord>(`/api/interview/records/${recordId}/rescore`, data)
}

// ==================== 面试结果汇总 ====================

// 获取场次面试结果汇总
export function getSessionResults(sessionId: number) {
  return get<InterviewResult[]>(`/api/interview/sessions/${sessionId}/results`)
}

// 设置候选人录取结果
export function setCandidateDecision(candidateId: number, data: {
  decision: 'PASS' | 'REJECT' | 'WAITLIST'
  position_id?: number
  notes?: string
}) {
  return post(`/api/interview/candidates/${candidateId}/decision`, data)
}

// ==================== 面试官任务 ====================

// 获取当前面试官的任务列表
export function getMyInterviewTasks() {
  return get<InterviewCandidate[]>('/api/interview/my-tasks')
}

// ==================== 文件上传 ====================

// 上传面试录音
export function uploadInterviewRecording(recordId: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return post<{ url: string }>(`/api/interview/records/${recordId}/upload-recording`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 上传候选人照片
export function uploadCandidateFace(recordId: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return post<{ url: string }>(`/api/interview/records/${recordId}/upload-face`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ==================== 通知 ====================

// 发送面试通知给候选人
export function sendInterviewNotification(sessionId: number, data: {
  candidate_ids?: number[] // 指定发送给哪些候选人，不传则发送给所有
  auto_send?: boolean // 是否自动发送
}) {
  return post(`/api/interview/sessions/${sessionId}/send-notification`, data)
}

// 候选人确认/拒绝面试
export function confirmInterview(interviewId: number, data: {
  status: 'CONFIRMED' | 'REJECTED'
}) {
  return put(`/api/interviews/${interviewId}/confirmation`, data)
}

// ==================== 学生端 ====================

// 获取学生的面试记录列表
export function getMyInterviewRecords(params?: {
  status?: InterviewCandidate['status']
  session_id?: number
}) {
  return get<InterviewCandidate[]>('/api/student/interviews', params)
}

// 获取学生的面试记录详情
export function getMyInterviewRecordDetail(candidateId: number) {
  return get<InterviewCandidate & { session?: InterviewSession; application?: SignupApplication }>(
    `/api/student/interviews/${candidateId}`
  )
}
