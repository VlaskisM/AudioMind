import { useQuery } from '@tanstack/react-query'
import { getRecordings } from '@/api/ingress'

export function useRecordings(offset = 0, limit = 50) {
  return useQuery({
    queryKey: ['recordings', offset, limit],
    queryFn: () => getRecordings(offset, limit),
    select: (response) => response.data,
    staleTime: 30_000,
  })
}
