import { useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { MessageSquare, Pencil, Check, X } from 'lucide-react'

interface ConversationListProps {
  conversations: ReturnType<typeof useChat>['conversations']
  activeId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onRename: (id: string, title: string) => void
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
  onRename,
}: ConversationListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')

  const startEdit = (id: string, title: string) => {
    setEditingId(id)
    setEditingTitle(title)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditingTitle('')
  }

  const saveEdit = (id: string) => {
    console.log('saveEdit called', { id, editingTitle })
    if (editingTitle.trim()) {
      console.log('Calling onRename', id, editingTitle.trim())
      onRename(id, editingTitle.trim())
    } else {
      console.log('editingTitle is empty, not calling onRename')
    }
    cancelEdit()
  }

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
                onClick={() => editingId !== conv.id && onSelect(conv.id)}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare className="h-4 w-4 shrink-0" />
                  {editingId === conv.id ? (
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') saveEdit(conv.id)
                        if (e.key === 'Escape') cancelEdit()
                      }}
                      className="flex-1 px-1 py-0.5 text-sm border rounded focus:outline-none focus:ring-1"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <span className="truncate text-sm">{conv.title}</span>
                  )}
                </div>
                {editingId === conv.id ? (
                  <div className="flex gap-1 ml-1">
                    <button
                      className="p-1 hover:bg-green-100 rounded transition-colors"
                      onClick={(e) => { e.stopPropagation(); saveEdit(conv.id) }}
                    >
                      <Check className="h-3 w-3 text-green-600" />
                    </button>
                    <button
                      className="p-1 hover:bg-red-100 rounded transition-colors"
                      onClick={(e) => { e.stopPropagation(); cancelEdit() }}
                    >
                      <X className="h-3 w-3 text-red-600" />
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      className="p-1 hover:bg-blue-100 rounded transition-colors"
                      onClick={(e) => {
                        e.stopPropagation()
                        startEdit(conv.id, conv.title)
                      }}
                    >
                      <Pencil className="h-3 w-3 text-muted-foreground hover:text-blue-600" />
                    </button>
                    <button
                      className="p-1 hover:bg-destructive/10 rounded transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDelete(conv.id)
                      }}
                    >
                      <span className="text-xs text-muted-foreground hover:text-destructive">×</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
