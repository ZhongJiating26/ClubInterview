import { get, post, put } from '../request'

export interface Ticket {
  id: number
  title: string
  content: string
  type: 'question' | 'feedback' | 'appeal' | 'other'
  status: 'pending' | 'replied' | 'closed'
  priority: 'low' | 'medium' | 'high'
  studentId: number
  studentName: string
  reply?: string
  repliedBy?: string
  repliedAt?: string
  createdAt: string
  updatedAt: string
}

export interface TicketListParams {
  page: number
  pageSize: number
  status?: string
  type?: string
  priority?: string
}

export interface CreateTicketParams {
  title: string
  content: string
  type: string
  priority?: string
}

export function getTicketList(params: TicketListParams) {
  return get('/api/tickets', params)
}

export function getTicketDetail(id: number) {
  return get(`/tickets/${id}`)
}

export function createTicket(data: CreateTicketParams) {
  return post('/api/tickets', data)
}

export function replyTicket(id: number, reply: string) {
  return put(`/tickets/${id}/reply`, { reply })
}

export function closeTicket(id: number) {
  return put(`/tickets/${id}/close`)
}

export function getMyTickets() {
  return get('/api/student/tickets')
}
