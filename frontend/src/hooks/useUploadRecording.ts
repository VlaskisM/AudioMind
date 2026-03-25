import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useMutation } from '@tanstack/react-query'
import { uploadRecording } from '@/api/ingress'

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
