import { useMutation, useQueryClient } from '@tanstack/react-query'
import { runAnalysis, type AnalysisType } from '@/api/analysis'

export function useAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ recordingId, type }: { recordingId: string; type: AnalysisType }) =>
      runAnalysis(recordingId, type),
    onSuccess: (response, { recordingId, type }) => {
      queryClient.setQueryData(['analysis', recordingId, type], response.data.data)
    },
  })
}
