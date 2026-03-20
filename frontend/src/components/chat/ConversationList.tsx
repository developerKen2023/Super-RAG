import { Conversation } from '@/hooks/useChat'
import { Button } from '@/components/ui/button'

interface ConversationListProps {
  conversations: Conversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onCreate: () => void
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
  onCreate,
}: ConversationListProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <Button onClick={onCreate} className="w-full">
          New Conversation
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-1 p-2">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`group flex items-center justify-between p-2 rounded-lg cursor-pointer hover:bg-accent ${
                activeId === conv.id ? 'bg-accent' : ''
              }`}
              onClick={() => onSelect(conv.id)}
            >
              <span className="truncate text-sm">{conv.title}</span>
              <Button
                variant="ghost"
                size="sm"
                className="opacity-0 group-hover:opacity-100 h-8 w-8 p-0"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(conv.id)
                }}
              >
                X
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
