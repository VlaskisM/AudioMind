import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'
import { Upload } from 'lucide-react'

const ACCEPTED_AUDIO = {
  'audio/mpeg': ['.mp3'],
  'audio/wav': ['.wav'],
  'audio/flac': ['.flac'],
  'audio/ogg': ['.ogg'],
  'audio/mp4': ['.m4a'],
  'audio/webm': ['.webm'],
}

interface UploadDropzoneProps {
  onFileAccepted: (file: File) => void
  disabled?: boolean
}

export function UploadDropzone({ onFileAccepted, disabled }: UploadDropzoneProps) {
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    accept: ACCEPTED_AUDIO,
    multiple: false,
    disabled,
    maxSize: 500 * 1024 * 1024, // 500MB
    onDropAccepted: (files) => onFileAccepted(files[0]),
  })

  return (
    <div>
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
          isDragActive && "border-primary bg-primary/5",
          disabled && "opacity-50 cursor-not-allowed",
          !isDragActive && !disabled && "border-muted-foreground/25 hover:border-primary/50"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-10 w-10 text-muted-foreground mb-4" />
        {isDragActive ? (
          <p className="text-primary font-medium">Отпустите файл...</p>
        ) : (
          <>
            <p className="font-medium">Перетащите аудиофайл или нажмите для выбора</p>
            <p className="text-sm text-muted-foreground mt-1">MP3, WAV, FLAC, OGG, M4A, WebM -- до 500 МБ</p>
          </>
        )}
      </div>
      {fileRejections.length > 0 && (
        <p className="text-sm text-destructive mt-2">
          Неподдерживаемый формат или файл слишком большой
        </p>
      )}
    </div>
  )
}
