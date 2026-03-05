import { get } from '../request'

export interface School {
  id: number
  name: string
  code: string
}

export interface SchoolSearchResult {
  total: number
  items: School[]
}

// 搜索学校
export function searchSchools(keyword: string) {
  return get<SchoolSearchResult>('/api/schools/search', { q: keyword })
}
