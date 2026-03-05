import { get, post, put } from '../request'

// 学生详细信息接口
export interface StudentProfile {
  id: number
  phone: string
  name: string | null
  email: string | null
  student_no: string | null
  major: string | null
  school_code: string | null
  school_name: string | null
  status: number
  is_initialized: boolean
  avatar_url: string | null
}

export interface StudentApplication {
  id: number
  department: string
  introduction: string
  status: 'pending' | 'approved' | 'rejected'
  applyTime: string
  remark?: string
}

export function getMyApplication() {
  return get('/api/student/application')
}

export function submitApplication(data: {
  department: string
  introduction: string
}) {
  return post('/api/student/application', data)
}

export function getMyInterviewInfo() {
  return get('/api/student/interview')
}

// 获取学生详细信息
export function getProfile() {
  return get<StudentProfile>('/api/student/profile')
}

// 更新学生个人资料
export function updateStudentProfile(data: {
  name?: string
  email?: string
  major?: string
  avatar_url?: string
}) {
  return put('/api/student/profile', data)
}

// ============ 学生端面试管理 ============

// 注意：面试相关的主要 API 已在 interview.ts 中定义
// 这里保留一些特定于学生端的辅助接口

// 获取面试结果（包含录取状态）
export function getInterviewResult(candidateId: number) {
  return get<{
    id: number
    status: 'pending' | 'admitted' | 'rejected'
    score: number | null
    feedback: string | null
  }>(`/api/student/interviews/${candidateId}/result`)
}
