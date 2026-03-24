import { useQuery } from '@tanstack/react-query'
import { getTranscript } from '@/api/analysis'

export function useTranscript(recordingId: string) {
  return useQuery({
    queryKey: ['transcript', recordingId],
    queryFn: () => getTranscript(recordingId),
    select: (response) => response.data.segments,
    staleTime: Infinity,
    enabled: !!recordingId,
  })
}
