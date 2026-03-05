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

export function updateProfile(data: {
  phone?: string
  email?: string
  nickname?: string
}) {
  return put('/api/student/profile', data)
}
