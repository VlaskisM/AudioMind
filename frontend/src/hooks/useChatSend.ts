import { useMutation, useQueryClient } from '@tanstack/react-query'
import { sendChatMessage } from '@/api/analysis'

export function useChatSend() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ recordingId, question }: { recordingId: string; question: string }) =>
      sendChatMessage(recordingId, question),
    onSuccess: (_response, { recordingId }) => {
      queryClient.invalidateQueries({ queryKey: ['chat-history', recordingId] })
    },
  })
}
