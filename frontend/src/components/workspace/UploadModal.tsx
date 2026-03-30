import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { UploadDropzone } from '@/components/UploadDropzone'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { useUploadInModal } from '@/hooks/useUploadRecording'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'
import { AxiosError } from 'axios'

export function UploadModal() {
  const open = useWorkspaceStore((s) => s.uploadModalOpen)
  const setOpen = useWorkspaceStore((s) => s.setUploadModalOpen)
  const { mutate, isPending, isError, error, reset, progress } = useUploadInModal()

  return (
    <Dialog open={open} onOpenChange={(nextOpen) => setOpen(nextOpen)}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Загрузите аудиофайл</DialogTitle>
        </DialogHeader>

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
      </DialogContent>
    </Dialog>
  )
}
