import { cn } from '@/lib/utils'
import { Check, Loader2, Circle } from 'lucide-react'

const STEPS = [
  { key: 'uploaded', label: 'Загружено' },
  { key: 'transcribing', label: 'Транскрибация' },
  { key: 'diarizing', label: 'Диаризация' },
  { key: 'ready', label: 'Готово' },
] as const

interface ProcessingStatusProps {
  currentStatus: string
}

export function ProcessingStatus({ currentStatus }: ProcessingStatusProps) {
  const currentIndex = STEPS.findIndex(s => s.key === currentStatus)

  return (
    <div className="space-y-4">
      {STEPS.map((step, i) => {
        const isDone = i < currentIndex
        const isActive = i === currentIndex
        const isPending = i > currentIndex

        return (
          <div
            key={step.key}
            className={cn(
              "flex items-center gap-3 text-sm",
              isDone && "text-muted-foreground",
              isActive && "text-primary font-medium",
              isPending && "text-muted-foreground/50"
            )}
          >
            {isDone && <Check className="h-5 w-5 text-primary" />}
            {isActive && <Loader2 className="h-5 w-5 animate-spin" />}
            {isPending && <Circle className="h-5 w-5" />}
            <span>{step.label}</span>
          </div>
        )
      })}
    </div>
  )
}
