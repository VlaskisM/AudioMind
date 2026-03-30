import { useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useAnalysis } from '@/hooks/useAnalysis'
import type {
  AnalysisType,
  SummaryData,
  KeyPoint,
  ActionItem,
  FaqItem,
} from '@/api/analysis'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

const TYPE_LABELS: Record<AnalysisType, string> = {
  summary: 'Краткое содержание',
  'key-points': 'Ключевые тезисы',
  'action-items': 'Задачи',
  faq: 'FAQ',
}

interface AnalysisResultProps {
  recordingId: string
  type: AnalysisType
}

export function AnalysisResult({ recordingId, type }: AnalysisResultProps) {
  const queryClient = useQueryClient()
  const mutation = useAnalysis()
  const [result, setResult] = useState<unknown>(null)

  useEffect(() => {
    const cached = queryClient.getQueryData(['analysis', recordingId, type])
    if (cached) setResult(cached)
  }, [queryClient, recordingId, type])

  function handleGenerate() {
    mutation.mutate(
      { recordingId, type },
      { onSuccess: (response) => setResult(response.data.data) },
    )
  }

  if (!result && !mutation.isPending) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4">
        {mutation.isError && (
          <p className="text-sm text-destructive">
            Ошибка генерации. Попробуйте ещё раз.
          </p>
        )}
        <p className="text-muted-foreground">
          Нажмите кнопку для генерации анализа
        </p>
        <Button onClick={handleGenerate}>
          Сгенерировать {TYPE_LABELS[type]}
        </Button>
      </div>
    )
  }

  if (mutation.isPending) {
    return (
      <div className="space-y-3 p-4">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-5/6" />
      </div>
    )
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4">
        {type === 'summary' && <SummaryView data={result as SummaryData} />}
        {type === 'key-points' && (
          <KeyPointsView
            data={(result as { key_points?: KeyPoint[] })?.key_points ?? []}
          />
        )}
        {type === 'action-items' && (
          <ActionItemsView
            data={
              (result as { action_items?: ActionItem[] })?.action_items ?? []
            }
          />
        )}
        {type === 'faq' && (
          <FaqView
            data={(result as { faq?: FaqItem[] })?.faq ?? []}
          />
        )}
      </div>
    </ScrollArea>
  )
}

function SummaryView({ data }: { data: SummaryData }) {
  return (
    <div className="space-y-4">
      <p className="text-sm leading-relaxed">{data.summary}</p>
      {data.topics?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {data.topics.map((topic, i) => (
            <Badge key={i} variant="secondary">
              {topic}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}

function KeyPointsView({ data }: { data: KeyPoint[] }) {
  if (!data.length) {
    return (
      <p className="text-sm text-muted-foreground">
        Ключевые тезисы не найдены.
      </p>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((item, i) => (
        <Card key={i}>
          <CardContent className="pt-4">
            <p className="text-sm">{item.point}</p>
            <Badge variant="outline" className="mt-2">
              {item.speaker}
            </Badge>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function ActionItemsView({ data }: { data: ActionItem[] }) {
  if (!data.length) {
    return (
      <p className="text-sm text-muted-foreground">Задачи не найдены.</p>
    )
  }

  return (
    <div className="space-y-3">
      {data.map((item, i) => (
        <Card key={i}>
          <CardContent className="pt-4">
            <p className="text-sm font-medium">{item.action}</p>
            <Badge variant="outline" className="mt-2">
              {item.assignee}
            </Badge>
            {item.context && (
              <p className="mt-2 text-xs text-muted-foreground">{item.context}</p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function FaqView({ data }: { data: FaqItem[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  if (!data.length) {
    return (
      <p className="text-sm text-muted-foreground">FAQ не найден.</p>
    )
  }

  return (
    <div className="space-y-2">
      {data.map((item, i) => (
        <div key={i} className="rounded-md border p-3">
          <button
            type="button"
            className="w-full text-left text-sm font-semibold"
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
          >
            {item.question}
          </button>
          {openIndex === i && (
            <p className="mt-2 text-sm text-muted-foreground">{item.answer}</p>
          )}
        </div>
      ))}
    </div>
  )
}
