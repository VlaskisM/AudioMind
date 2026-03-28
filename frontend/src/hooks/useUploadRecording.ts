import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadRecording } from '@/api/ingress'
import { useWorkspaceStore } from '@/stores/workspaceStore'

export function useUploadRecording() {
  const [progress, setProgress] = useState(0)
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: (file: File) => uploadRecording(file, setProgress),
    onSuccess: (response) => {
      navigate(`/recordings/${response.data.id}/processing`)
    },
    onSettled: () => {
      setProgress(0)
    },
  })

  return { ...mutation, progress }
}

export function useUploadInModal() {
  const [progress, setProgress] = useState(0)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (file: File) => uploadRecording(file, setProgress),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] })
      useWorkspaceStore.getState().setUploadModalOpen(false)
      navigate(`/recordings/${response.data.id}`)
    },
    onSettled: () => {
      setProgress(0)
    },
  })

  return { ...mutation, progress }
}
