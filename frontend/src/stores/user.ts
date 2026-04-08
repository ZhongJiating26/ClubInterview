import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe, type UserInfo } from '@/api/modules/auth'

export type UserRole = 'admin' | 'interviewer' | 'student'

export interface UserProfile extends UserInfo {
  primaryRole: UserRole | null
}

type RoleCode = string

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  // 获取主角色（优先级：社团管理员 > 面试官 > 普通学生）
  const primaryRole = computed(() => {
    if (!userInfo.value?.roles.length) return null
    const roleCodes = userInfo.value.roles.map(r => r.code)
    // 后端返回的 code 格式：CLUB_ADMIN, INTERVIEWER, STUDENT
    if (roleCodes.includes('CLUB_ADMIN') || roleCodes.includes('admin')) return 'admin'
    if (roleCodes.includes('INTERVIEWER') || roleCodes.includes('interviewer')) return 'interviewer'
    if (roleCodes.includes('STUDENT') || roleCodes.includes('student')) return 'student'
    return null
  })

  // 设置 token
  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  // 设置用户信息
  function setUserInfo(info: UserInfo) {
    userInfo.value = info
  }

  // 登录
  async function doLogin(phone: string, password: string) {
    const res = await loginApi({ phone, password })
    setToken(res.access_token)

    // 获取用户信息
    const userData = await getMe()
    setUserInfo(userData)

    return res
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  // 判断是否有某个角色
  function hasRole(role: UserRole): boolean {
    if (!userInfo.value?.roles.length) return false
    return userInfo.value.roles.some(r => r.code === role)
  }

  // 判断是否有任意角色
  function hasAnyRole(roles: UserRole[]): boolean {
    if (!userInfo.value?.roles.length) return false
    return userInfo.value.roles.some(r => roles.includes(r.code as UserRole))
  }

  // 获取某个角色关联的社团 ID，优先返回带 club_id 的记录
  function getClubIdByRoleCode(roleCode: RoleCode): number | null {
    if (!userInfo.value?.roles.length) return null

    const exactMatchWithClub = userInfo.value.roles.find(
      (role) => role.code === roleCode && role.club_id !== null && role.club_id !== undefined
    )
    if (exactMatchWithClub) return exactMatchWithClub.club_id

    const exactMatch = userInfo.value.roles.find((role) => role.code === roleCode)
    return exactMatch?.club_id ?? null
  }

  return {
    token,
    userInfo,
    primaryRole,
    setToken,
    setUserInfo,
    doLogin,
    logout,
    hasRole,
    hasAnyRole,
    getClubIdByRoleCode
  }
})
