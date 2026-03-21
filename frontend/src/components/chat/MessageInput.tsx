import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Plus } from 'lucide-react'

interface MessageInputProps {
  onSend: (content: string) => Promise<void>
  onNewChat?: () => void
  disabled?: boolean
}

export function MessageInput({ onSend, onNewChat, disabled }: MessageInputProps) {
  const [content, setContent] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim() || disabled) return

    await onSend(content.trim())
    setContent('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="space-y-2">
      {onNewChat && (
        <div className="flex justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={onNewChat}
            className="h-7 text-xs"
          >
            <Plus className="h-3 w-3 mr-1" />
            New Chat
          </Button>
        </div>
      )}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="min-h-[44px] max-h-[150px] resize-none"
          disabled={disabled}
        />
        <Button type="submit" disabled={!content.trim() || disabled} className="shrink-0">
          Send
        </Button>
      </form>
    </div>
  )
}
