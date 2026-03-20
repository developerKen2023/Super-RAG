import { useEffect } from 'react'
import { useChat } from '@/hooks/useChat'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ConversationList } from '@/components/chat/ConversationList'
import { useAuth } from '@/hooks/useAuth'

export function ChatPage() {
  const { user } = useAuth()
  const {
    conversations,
    activeConversationId,
    loadConversations,
    loadMessages,
    createConversation,
    deleteConversation,
  } = useChat()

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  return (
    <div className="flex h-screen">
      <div className="w-64 border-r flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-semibold">Conversations</h2>
          <p className="text-sm text-muted-foreground">{user?.email}</p>
        </div>
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={loadMessages}
          onDelete={deleteConversation}
          onCreate={createConversation}
        />
      </div>

      <div className="flex-1 flex flex-col">
        <ChatWindow />
      </div>
    </div>
  )
}
