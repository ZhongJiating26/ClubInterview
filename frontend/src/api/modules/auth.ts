import { get, post } from '../request'

export interface LoginParams {
  phone: string
  password: string
}

export interface LoginResult {
  access_token: string
  token_type: string
}

export interface UserRoleInfo {
  id: number
  code: string
  name: string
  club_id: number | null
}

export interface UserInfo {
  id: number
  phone: string
  name: string | null
  status: number
  is_initialized: boolean
  roles: UserRoleInfo[]
  school_code?: string | null
  school_name?: string | null
}

// 发送验证码
export function sendCode(data: { phone: string; scene: 'REGISTER' | 'LOGIN' }) {
  return post<{ message: string; dev_code: string | null }>('/api/auth/send-code', data)
}

// 注册（返回 access_token）
export function register(data: { phone: string; code: string }) {
  return post<{ access_token: string; token_type: string }>('/api/auth/register', data)
}

export function login(data: LoginParams) {
  return post<LoginResult>('/api/auth/login', data)
}

export function getMe() {
  return get<UserInfo>('/api/auth/me')
}

// 初始化账号（需要 token）
export function initAccount(data: {
  password: string
  name: string
  id_card_no: string
  school_code: string
  major: string
  student_no: string
  role: string
  club_name?: string
  email?: string
  avatar_url?: string
}) {
  return post<{ detail: string }>('/api/auth/init', data)
}

// 分配角色（需要 token）
export function assignRole(data: {
  user_id: number
  role_id: number
  club_id?: number | null
}) {
  return post<{ detail: string; user_role: { id: number; user_id: number; role_id: number; club_id: number | null } }>('/api/auth/assign-role', data)
}

// 社团管理员创建社团（需要 token）
export function initClub(data: {
  club_name: string
  school_code: string
}) {
  return post<{ detail: string; club_id: number; is_new: boolean }>('/api/clubs/init', data)
}

// ============ 认证增强功能 ============

// 修改密码
export function changePassword(data: {
  old_password: string
  new_password: string
}) {
  return post<{ detail: string }>('/api/auth/change-password', data)
}

// 忘记密码 - 发送验证码
export function forgotPassword(data: { phone: string }) {
  return post<{ detail: string }>('/api/auth/forgot-password', data)
}

// 重置密码
export function resetPassword(data: {
  phone: string
  code: string
  new_password: string
}) {
  return post<{ detail: string }>('/api/auth/reset-password', data)
}

// 注销账号
export function deleteAccount(data: {
  password: string
  confirmation: string
}) {
  return post<{ detail: string }>('/api/auth/account/delete', data)
}
