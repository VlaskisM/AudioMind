interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  quote?: string
}

export function ChatMessage({ role, content, quote }: ChatMessageProps) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-lg bg-muted px-3 py-2 text-sm">
          {content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="flex max-w-[80%] flex-col gap-1">
        <div className="text-sm">{content}</div>
        {quote && (
          <blockquote className="border-l-2 border-primary pl-3 text-sm italic text-muted-foreground">
            {quote}
          </blockquote>
        )}
      </div>
    </div>
  )
}
