import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

export const analysisApi = axios.create({
  baseURL: '/api/analysis',
})

analysisApi.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

analysisApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Types
export interface SummaryData {
  summary: string
  topics: string[]
}

export interface KeyPoint {
  point: string
  speaker: string
}

export interface ActionItem {
  action: string
  assignee: string
  context: string
}

export interface FaqItem {
  question: string
  answer: string
}

export interface ChatAnswer {
  answer: string
  quote: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface TranscriptSegment {
  speaker: string
  start: number
  end: number
  text: string
}

export type AnalysisType = 'summary' | 'key-points' | 'action-items' | 'faq'

// API functions
export function runAnalysis(recordingId: string, type: AnalysisType) {
  return analysisApi.post(`/analysis/${recordingId}/${type}`)
}

export function sendChatMessage(recordingId: string, question: string) {
  return analysisApi.post(`/analysis/${recordingId}/chat`, { question })
}

export function getChatHistory(recordingId: string) {
  return analysisApi.get(`/analysis/${recordingId}/chat/history`)
}

export function getTranscript(recordingId: string) {
  return analysisApi.get(`/analysis/recordings/${recordingId}/transcript`)
}
