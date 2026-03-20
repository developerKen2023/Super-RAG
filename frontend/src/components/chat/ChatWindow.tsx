import { useChat } from '@/hooks/useChat'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

export function ChatWindow() {
  const {
    currentMessages,
    streamingContent,
    loading,
    sendMessage,
  } = useChat()

  const handleSend = async (content: string) => {
    await sendMessage(content)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        <MessageList
          messages={currentMessages}
          streamingContent={streamingContent}
        />
      </div>
      <div className="border-t p-4">
        <MessageInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  )
}
