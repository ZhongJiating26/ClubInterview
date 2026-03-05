import { get, put } from '../request'

export interface Notification {
  id: number
  title: string
  content: string
  type: 'application' | 'interview' | 'result' | 'system'
  isRead: boolean
  relatedId?: number
  createdAt: string
}

export function getNotificationList(params?: { page?: number; pageSize?: number; isRead?: boolean }) {
  return get('/api/notifications', params)
}

export function getUnreadCount() {
  return get('/api/notifications/unread-count')
}

export function markAsRead(id: number) {
  return put(`/notifications/${id}/read`)
}

export function markAllAsRead() {
  return put('/api/notifications/read-all')
}
