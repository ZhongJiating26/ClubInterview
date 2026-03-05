import { get, post, put } from '../request'

export interface ScoreItem {
  id: number
  interviewResultId: number
  criterionId: number
  criterionName: string
  score: number
  maxScore: number
  remark?: string
}

export interface ScoreParams {
  interviewResultId: number
  scores: {
    criterionId: number
    score: number
    remark?: string
  }[]
  remark?: string
}

export function getScoreCriteria(department: string) {
  return get('/api/score/criteria', { department })
}

export function submitScore(data: ScoreParams) {
  return post('/api/score', data)
}

export function getScoreDetail(resultId: number) {
  return get(`/score/${resultId}`)
}

export function updateScore(resultId: number, data: ScoreParams) {
  return put(`/score/${resultId}`, data)
}
