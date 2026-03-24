import { useParams, useNavigate } from 'react-router'
import { useEffect } from 'react'
import { useRecordingStatus } from '@/hooks/useRecordingStatus'
import { ProcessingStatus } from '@/components/ProcessingStatus'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

export default function ProcessingPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data, isError } = useRecordingStatus(id!)

  // Auto-redirect when ready
  useEffect(() => {
    if (data?.status === 'ready') {
      navigate(`/recordings/${id}`, { replace: true })
    }
  }, [data?.status, id, navigate])

  // Network or request error
  if (isError) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4 max-w-md px-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Ошибка соединения</AlertTitle>
            <AlertDescription>
              Не удалось получить статус записи. Проверьте соединение с сервером.
            </AlertDescription>
          </Alert>
          <Button onClick={() => navigate('/')}>Загрузить другой файл</Button>
        </div>
      </div>
    )
  }

  const currentStatus = data?.status ?? 'uploaded'

  // Backend returned failed status
  if (currentStatus === 'failed') {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4 max-w-md px-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Ошибка обработки</AlertTitle>
            <AlertDescription>
              {data?.error_message || 'Произошла ошибка при обработке записи'}
            </AlertDescription>
          </Alert>
          <Button onClick={() => navigate('/')}>Загрузить другой файл</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-6 max-w-md px-4">
        <h1 className="text-2xl font-bold">Обработка записи</h1>
        <ProcessingStatus currentStatus={currentStatus} />
        <p className="text-sm text-muted-foreground">Это может занять несколько минут</p>
      </div>
    </div>
  )
}
