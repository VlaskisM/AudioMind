import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

export const ingressApi = axios.create({
  baseURL: '/api/ingress',
})

ingressApi.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

ingressApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface RecordingResponse {
  id: number
  ts: number
  file_url: string
  user_id: number
  status: string
  original_filename: string | null
}

export interface Recording {
  id: number
  ts: number
  file_url: string
  user_id: number
  status: string
  original_filename: string | null
}

export interface PaginatedResponse {
  data: Recording[]
  total: number
  offset: number
  limit: number
}

export function getRecordings(offset = 0, limit = 50) {
  return ingressApi.get<PaginatedResponse>('/recordings/', { params: { offset, limit } })
}

export function deleteRecording(recordingId: number) {
  return ingressApi.delete(`/recordings/${recordingId}`)
}

export function uploadRecording(
  file: File,
  onProgress?: (percent: number) => void
) {
  const formData = new FormData()
  formData.append('file', file)

  return ingressApi.post<RecordingResponse>(
    '/recordings/upload',
    formData,
    {
      timeout: 0,
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      },
    }
  )
}
