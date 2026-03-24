import { useQuery } from '@tanstack/react-query'
import { getChatHistory } from '@/api/analysis'

export function useChatHistory(recordingId: string) {
  return useQuery({
    queryKey: ['chat-history', recordingId],
    queryFn: () => getChatHistory(recordingId),
    select: (response) => response.data.data,
    enabled: !!recordingId,
  })
}
