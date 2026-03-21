import { useEffect, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ConversationList } from '@/components/chat/ConversationList'
import { DocumentUpload, DocumentList } from '@/components/documents'
import { documentsApi } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'

type Tab = 'chat' | 'documents'

export function ChatPage() {
  const { user } = useAuth()
  const {
    conversations,
    activeConversationId,
    currentMessages,
    streamingContent,
    loading,
    loadConversations,
    loadMessages,
    deleteConversation,
    sendMessage,
    createConversation,
  } = useChat()

  const [tab, setTab] = useState<Tab>('chat')
  const [token, setToken] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [docsLoading, setDocsLoading] = useState(false)

  useEffect(() => {
    const getToken = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setToken(session?.access_token ?? null)
    }
    getToken()
  }, [])

  const loadDocuments = async () => {
    if (!token) return
    setDocsLoading(true)
    try {
      const docs = await documentsApi.list(token)
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setDocsLoading(false)
    }
  }

  const handleDeleteDocument = async (id: string) => {
    if (!token) return
    try {
      await documentsApi.delete(token, id)
      setDocuments(prev => prev.filter(d => d.id !== id))
    } catch (error) {
      console.error('Failed to delete document:', error)
    }
  }

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  useEffect(() => {
    if (token) {
      loadDocuments()
    }
  }, [token])

  // Reload documents when switching to documents tab
  useEffect(() => {
    if (tab === 'documents' && token) {
      loadDocuments()
    }
  }, [tab, token])

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 border-r flex flex-col bg-muted/30">
        {/* Header */}
        <div className="p-4 border-b">
          <h1 className="font-semibold text-lg">Agentic RAG</h1>
          <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setTab('chat')}
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              tab === 'chat' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Chat
          </button>
          <button
            onClick={() => setTab('documents')}
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              tab === 'documents' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Documents
          </button>
        </div>

        {/* Content */}
        {tab === 'chat' ? (
          <ConversationList
            conversations={conversations}
            activeId={activeConversationId}
            onSelect={loadMessages}
            onDelete={deleteConversation}
          />
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <DocumentUpload token={token} onUploadComplete={loadDocuments} />
            <DocumentList
              documents={documents}
              onDelete={handleDeleteDocument}
              loading={docsLoading}
            />
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {tab === 'chat' ? (
          <ChatWindow
            currentMessages={currentMessages}
            streamingContent={streamingContent}
            loading={loading}
            onSendMessage={sendMessage}
            onNewChat={createConversation}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            <p>Select a conversation to start chatting</p>
          </div>
        )}
      </div>
    </div>
  )
}

interface Document {
  id: string
  user_id: string
  filename: string
  file_path: string
  file_size: number
  mime_type: string
  status: string
  chunk_count: number
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}
