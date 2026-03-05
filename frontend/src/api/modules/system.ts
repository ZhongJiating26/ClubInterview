import { get } from '../request'

// ==================== 类型定义 ====================

// 系统角色
export interface SystemRole {
  code: string
  name: string
  description: string
  icon?: string
  sort_order: number
}

// 社团分类
export interface ClubCategory {
  id: string
  name: string
  description?: string
  sort_order: number
}

// 系统配置项
export interface SystemConfig {
  key: string
  value: any
  description?: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
}

// ==================== 系统角色 ====================

// 获取系统角色列表
export function getSystemRoles() {
  return get<SystemRole[]>('/api/system/roles')
}

// ==================== 社团分类 ====================

// 获取社团分类列表
export function getClubCategories() {
  return get<ClubCategory[]>('/api/system/club-categories')
}

// ==================== 系统配置 ====================

// 获取系统配置
export function getSystemConfig(key?: string) {
  return get<SystemConfig | SystemConfig[]>('/api/system/config', { key })
}

// 获取多个系统配置
export function getSystemConfigs(keys: string[]) {
  return get<Record<string, any>>('/api/system/configs', { keys: keys.join(',') })
}

// ==================== 通用 ====================

// 获取学校列表
export function getSchools() {
  return get<Array<{ code: string; name: string }>>('/api/system/schools')
}
