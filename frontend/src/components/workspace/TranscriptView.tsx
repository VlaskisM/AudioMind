import { useTranscript } from '@/hooks/useTranscript'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

const SPEAKER_COLORS = [
  'bg-blue-100 text-blue-800',
  'bg-green-100 text-green-800',
  'bg-purple-100 text-purple-800',
  'bg-orange-100 text-orange-800',
  'bg-pink-100 text-pink-800',
  'bg-teal-100 text-teal-800',
  'bg-red-100 text-red-800',
  'bg-yellow-100 text-yellow-800',
]

function speakerColor(speaker: string): string {
  let hash = 0
  for (let i = 0; i < speaker.length; i++) {
    hash = (hash * 31 + speaker.charCodeAt(i)) | 0
  }
  return SPEAKER_COLORS[Math.abs(hash) % SPEAKER_COLORS.length]
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

interface TranscriptViewProps {
  recordingId: string
}

export function TranscriptView({ recordingId }: TranscriptViewProps) {
  const { data: segments, isLoading } = useTranscript(recordingId)

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (!segments || segments.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        Транскрипция не найдена
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-3 p-4">
        {segments.map((segment, index) => (
          <div
            key={index}
            className={`flex flex-col gap-1 pb-3 ${index < segments.length - 1 ? 'border-b' : ''}`}
          >
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={speakerColor(segment.speaker)}>
                {segment.speaker}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {formatTime(segment.start)} - {formatTime(segment.end)}
              </span>
            </div>
            <p className="text-sm">{segment.text}</p>
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}
