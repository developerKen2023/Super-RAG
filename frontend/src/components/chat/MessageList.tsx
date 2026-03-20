import { Message } from '@/hooks/useChat'

interface MessageListProps {
  messages: Message[]
  streamingContent: string
}

export function MessageList({ messages, streamingContent }: MessageListProps) {
  return (
    <div className="space-y-4 p-4">
      {messages.length === 0 && (
        <div className="text-center text-muted-foreground py-8">
          <p>No messages yet. Start a conversation!</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
            <span className="text-xs opacity-50 mt-1 block">
              {new Date(message.created_at).toLocaleTimeString()}
            </span>
          </div>
        </div>
      ))}

      {streamingContent && (
        <div className="flex justify-start">
          <div className="max-w-[70%] rounded-lg px-4 py-2 bg-muted">
            <p className="whitespace-pre-wrap">{streamingContent}</p>
            <span className="text-xs opacity-50 mt-1 block animate-pulse">
              Typing...
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
