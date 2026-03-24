import { useState, useRef, useEffect } from 'react'
import { useChatHistory } from '@/hooks/useChatHistory'
import { useChatSend } from '@/hooks/useChatSend'
import { ChatMessage } from '@/components/workspace/ChatMessage'
import { ChatInput } from '@/components/workspace/ChatInput'
import { ScrollArea } from '@/components/ui/scroll-area'

interface OptimisticMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatPanelProps {
  recordingId: string
}

export function ChatPanel({ recordingId }: ChatPanelProps) {
  const { data: history } = useChatHistory(recordingId)
  const { mutate, isPending } = useChatSend()
  const [optimistic, setOptimistic] = useState<OptimisticMessage[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)

  const messages = history ?? []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, optimistic.length])

  function handleSend(question: string) {
    setOptimistic((prev) => [...prev, { role: 'user', content: question }])
    mutate(
      { recordingId, question },
      {
        onSuccess: () => {
          setOptimistic([])
        },
        onError: () => {
          setOptimistic((prev) => prev.slice(0, -1))
          console.error('Failed to send chat message')
        },
      },
    )
  }

  const hasMessages = messages.length > 0 || optimistic.length > 0

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 p-4">
        {!hasMessages ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            Задайте вопрос по содержанию записи
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg, i) => (
              <ChatMessage key={i} role={msg.role} content={msg.content} />
            ))}
            {optimistic.map((msg, i) => (
              <ChatMessage key={`opt-${i}`} role={msg.role} content={msg.content} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </ScrollArea>
      <ChatInput onSend={handleSend} disabled={isPending} />
    </div>
  )
}
