import request, { get, post } from '../request'

// 搜索用户结果
export interface SearchedUser {
  id: number
  name: string | null
  phone: string
}

// 邀请状态
export type InvitationStatus = 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED' | 'REMOVED'

// 面试官邀请
export interface InterviewerInvitation {
  id: number
  club_id: number
  club_name: string
  club_logo_url?: string
  user_id: number
  inviter_name?: string
  status: InvitationStatus
  invite_code: string
  created_at: string
}

// 社团面试官
export interface ClubInterviewer {
  id: number
  name: string
  phone: string
  email?: string
  role_name?: string
  joined_at: string
}

interface ClubMemberItem {
  user_id: number
  user_name: string
  user_phone: string
  user_email?: string
  role_id: number
  role_name: string
  club_id: number
  joined_at: string
}

interface ClubMembersResponse {
  items: ClubMemberItem[]
  total: number
}

// ==================== 管理员端 ====================

// 获取社团的面试官列表
export async function getClubInterviewers(clubId: number) {
  const res = await get<ClubMembersResponse>(`/api/clubs/${clubId}/members`)

  return res.items
    .filter((member) => member.role_id === 3 || member.role_name === '面试官')
    .map((member) => ({
      id: member.user_id,
      name: member.user_name,
      phone: member.user_phone,
      email: member.user_email,
      role_name: member.role_name,
      joined_at: member.joined_at,
    }))
}

export function removeClubInterviewer(clubId: number, userId: number) {
  return request.delete<{ detail: string }>(`/api/clubs/${clubId}/interviewers/${userId}`)
}

// 搜索用户
export async function searchUsers(params: { phone: string }) {
  const res = await get<any>('/api/admin/users/search', params)
  // 后端返回格式: {items: [...], total: 1}
  if (res && typeof res === 'object' && 'items' in res) {
    return res.items as SearchedUser[]
  }
  // 兼容其他可能的格式
  if (res && typeof res === 'object' && 'data' in res) {
    return res.data as SearchedUser[]
  }
  return res as SearchedUser[]
}

// 发送面试官邀请
export function inviteInterviewer(clubId: number, data: { user_id: number }) {
  return post<InterviewerInvitation>(`/api/admin/clubs/${clubId}/invite-interviewer`, data)
}

// ==================== 面试官端 ====================

// 获取我的邀请列表
export function getMyInvitations() {
  return get<InterviewerInvitation[]>('/api/interviewer/invitations')
}

// 接受邀请
export function acceptInvitation(invitationId: number) {
  return post<{ detail: string }>(`/api/interviewer/invitations/${invitationId}/accept`)
}

// 拒绝邀请
export function rejectInvitation(invitationId: number, reason?: string) {
  return post<{ detail: string }>(`/api/interviewer/invitations/${invitationId}/reject`, {
    reason
  })
}
