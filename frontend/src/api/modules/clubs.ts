import axios, { get, post, put, del } from '../request'

export interface ClubInfo {
  id: number
  school_name: string
  name: string
  logo_url: string
  category: string
  description: string | null
  cert_file_url: string | null
  status: string
  created_at: string
  recruiting_status?: 'RECRUITING' | 'NO_RECRUITMENT'
}

export interface ClubHomeInfo {
  id: number
  name: string
  logo_url: string
  description: string | null
  category: string
  school_name: string
  status: string
  recruiting_status: 'RECRUITING' | 'NO_RECRUITMENT'
}

export interface ClubProfileCheckResponse {
  club_id: number
  is_complete: boolean
  missing_fields: string[]
}

export interface ClubCheckResponse {
  exists: boolean
  club_id: number | null
  message: string
}

// 部门相关接口
export interface Department {
  id: number
  club_id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

// 岗位相关接口
export interface Position {
  id: number
  club_id: number
  department_id: number | null
  name: string
  description: string | null
  requirement: string | null
  created_at: string
  updated_at: string
}

// 社团资料检查
export function checkClubProfile(clubId: number) {
  return get<ClubProfileCheckResponse>(`/api/clubs/${clubId}/profile-check`)
}

// 检查社团是否存在
export function checkClub(data: { club_name: string; school_code: string }) {
  return post<ClubCheckResponse>('/api/clubs/check', data)
}

// 将用户关联到社团
export function bindUserToClub(clubId: number, data: { user_id: number; role_code: string }) {
  return post(`/api/clubs/${clubId}/bind-user`, data)
}

// 获取社团详情
export function getClub(clubId: number) {
  return get<ClubInfo>(`/api/clubs/${clubId}`)
}

// 获取学校社团列表（首页展示用）
export function getClubsBySchool(params: {
  school_code: string
  status?: string
}) {
  return get<ClubHomeInfo[]>('/api/clubs/home-list', params)
}

// 社团详情页数据（扁平结构，包含部门、岗位、招新场次）
export interface ClubDetailData extends ClubInfo {
  departments: Department[]
  positions: Position[]
  recruitment_sessions: any[] // 招新场次列表
}

export function getClubDetail(clubId: number) {
  return get<ClubDetailData>(`/api/clubs/${clubId}/detail`)
}

// 更新社团信息（支持传文件）
export function updateClub(clubId: number, data: {
  name?: string
  category?: string
  description?: string
  logo?: File | null
  cert_file?: File | null
}) {
  // 如果有文件，使用 multipart/form-data
  if (data.logo || data.cert_file) {
    const formData = new FormData()
    if (data.name !== undefined) formData.append('name', data.name)
    if (data.category !== undefined) formData.append('category', data.category)
    if (data.description !== undefined) formData.append('description', data.description)
    if (data.logo) formData.append('logo', data.logo)
    if (data.cert_file) formData.append('cert_file', data.cert_file)
    return axios.put(`/api/clubs/${clubId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }

  // 否则使用 JSON
  return put(`/api/clubs/${clubId}`, {
    name: data.name,
    category: data.category,
    description: data.description
  })
}

// ==================== 部门管理 ====================

// 获取部门列表
export function getDepartments(clubId: number) {
  return get<Department[]>(`/api/clubs/${clubId}/departments`)
}

// 创建部门
export function createDepartment(clubId: number, data: {
  name: string
  description?: string
}) {
  return post<Department>(`/api/clubs/${clubId}/departments`, data)
}

// 更新部门
export function updateDepartment(clubId: number, deptId: number, data: {
  name?: string
  description?: string
}) {
  return put<Department>(`/api/clubs/${clubId}/departments/${deptId}`, data)
}

// 删除部门
export function deleteDepartment(clubId: number, deptId: number) {
  return del(`/api/clubs/${clubId}/departments/${deptId}`)
}

// ==================== 岗位管理 ====================

// 获取岗位列表
export function getPositions(clubId: number, params?: { department_id?: number }) {
  return get<Position[]>(`/api/clubs/${clubId}/positions`, params)
}

// 创建岗位
export function createPosition(clubId: number, data: {
  department_id?: number
  name: string
  description?: string
  requirement?: string
}) {
  return post<Position>(`/api/clubs/${clubId}/positions`, data)
}

// 更新岗位
export function updatePosition(clubId: number, posId: number, data: {
  name?: string
  description?: string
  requirement?: string
}) {
  return put<Position>(`/api/clubs/${clubId}/positions/${posId}`, data)
}

// 删除岗位
export function deletePosition(clubId: number, posId: number) {
  return del(`/api/clubs/${clubId}/positions/${posId}`)
}
