import { useState } from 'react'
import { SendHorizonal } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface ChatInputProps {
  onSend: (question: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t p-4">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Задайте вопрос по записи..."
        disabled={disabled}
      />
      <Button
        type="submit"
        size="icon"
        disabled={disabled || !value.trim()}
      >
        <SendHorizonal className="h-4 w-4" />
      </Button>
    </form>
  )
}
