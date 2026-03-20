import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { Message } from '@/hooks/useChat'

interface ChatWindowProps {
  currentMessages: Message[]
  streamingContent: string
  loading: boolean
  onSendMessage: (content: string) => Promise<void>
}

export function ChatWindow({
  currentMessages,
  streamingContent,
  loading,
  onSendMessage,
}: ChatWindowProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        <MessageList
          messages={currentMessages}
          streamingContent={streamingContent}
        />
      </div>
      <div className="border-t p-4">
        <MessageInput onSend={onSendMessage} disabled={loading} />
      </div>
    </div>
  )
}
