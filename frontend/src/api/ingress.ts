import axios from 'axios'

export const ingressApi = axios.create({
  baseURL: '/api/ingress',
})

export interface RecordingResponse {
  status: string
  data: {
    id: number
    user_id: number
    status: string
    original_filename: string
  }
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

export function uploadRecording(
  file: File,
  onProgress?: (percent: number) => void
) {
  const formData = new FormData()
  formData.append('file', file)

  return ingressApi.post<RecordingResponse>(
    '/recordings/upload?user_id=1',
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
