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
