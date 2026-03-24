import { useQuery } from '@tanstack/react-query'
import { ingressApi } from '@/api/ingress'

export interface RecordingStatusData {
  id: number
  status: 'uploaded' | 'transcribing' | 'diarizing' | 'ready' | 'failed'
  error_message: string | null
}

interface StatusResponse {
  status: string
  data: RecordingStatusData
}

export function useRecordingStatus(recordingId: string) {
  return useQuery({
    queryKey: ['recording-status', recordingId],
    queryFn: () => ingressApi.get<StatusResponse>(`/recordings/${recordingId}/status`),
    refetchInterval: (query) => {
      const status = query.state.data?.data?.data?.status
      // Stop polling at terminal state
      if (status === 'ready' || status === 'failed') return false
      return 2000 // poll every 2 seconds
    },
    select: (response) => response.data.data,
  })
}
