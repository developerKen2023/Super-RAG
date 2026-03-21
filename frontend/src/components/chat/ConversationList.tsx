import { useChat } from '@/hooks/useChat'
import { MessageSquare } from 'lucide-react'

interface ConversationListProps {
  conversations: ReturnType<typeof useChat>['conversations']
  activeId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
}: ConversationListProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            <MessageSquare className="mx-auto h-8 w-8 mb-2 opacity-50" />
            <p>No conversations yet</p>
            <p className="text-xs mt-1">Start chatting below</p>
          </div>
        ) : (
          <div className="p-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors mb-1 ${
                  activeId === conv.id
                    ? 'bg-primary/10 text-primary'
                    : 'hover:bg-accent'
                }`}
                onClick={() => onSelect(conv.id)}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <MessageSquare className="h-4 w-4 shrink-0" />
                  <span className="truncate text-sm">{conv.title}</span>
                </div>
                <button
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(conv.id)
                  }}
                >
                  <span className="text-xs text-muted-foreground hover:text-destructive">×</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
