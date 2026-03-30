import { useNavigate } from 'react-router'
import { useUploadRecording } from '@/hooks/useUploadRecording'
import { useAuthStore } from '@/stores/authStore'
import { UploadDropzone } from '@/components/UploadDropzone'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AlertCircle, LogOut } from 'lucide-react'
import { AxiosError } from 'axios'

export default function UploadPage() {
  const { mutate, isPending, isError, error, reset, progress } = useUploadRecording()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  return (
    <div className="relative flex h-screen items-center justify-center">
      <div className="absolute right-4 top-4 flex items-center gap-2">
        <span className="text-sm text-muted-foreground">{user?.email}</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => {
            logout()
            navigate('/login')
          }}
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex flex-col gap-6 w-full max-w-lg px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Загрузите аудиофайл</h1>
          <p className="text-muted-foreground mt-1">Файл будет транскрибирован и проанализирован</p>
        </div>

        <UploadDropzone
          onFileAccepted={(file) => mutate(file)}
          disabled={isPending}
        />

        {isPending && (
          <div className="space-y-2">
            <Progress value={progress} />
            <p className="text-sm text-muted-foreground text-center">
              {progress < 100 ? `Загрузка: ${progress}%` : 'Обработка...'}
            </p>
          </div>
        )}

        {isError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Ошибка загрузки</AlertTitle>
            <AlertDescription className="flex flex-col gap-2">
              <span>
                {error instanceof AxiosError
                  ? error.response?.data?.detail || error.message
                  : 'Не удалось загрузить файл'}
              </span>
              <Button variant="outline" size="sm" className="self-start" onClick={() => reset()}>
                Попробовать снова
              </Button>
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  )
}
