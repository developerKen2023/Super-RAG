import { useEffect, useState, useCallback, useRef } from 'react'
import { useChat } from '@/hooks/useChat'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ConversationList } from '@/components/chat/ConversationList'
import { DocumentUpload } from '@/components/documents'
import { DocumentsView } from '@/components/documents/DocumentsView'
import { documentsApi } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { LogOut } from 'lucide-react'
import { logger } from '@/lib/logger'

type Tab = 'chat' | 'documents'

export function ChatPage() {
  const { user, logout } = useAuth()
  const {
    conversations,
    activeConversationId,
    currentMessages,
    streamingContent,
    loading,
    loadConversations,
    loadMessages,
    deleteConversation,
    renameConversation,
    sendMessage,
    createConversation,
  } = useChat()

  const [tab, setTab] = useState<Tab>('chat')
  const [token, setToken] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [docsLoading, setDocsLoading] = useState(false)

  // Resizable split pane state
  const [splitPos, setSplitPos] = useState(50) // percentage
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleLogout = () => {
    if (window.confirm('Are you sure to logout?')) {
      logout()
    }
  }

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const newPos = ((e.clientX - rect.left) / rect.width) * 100
    // Clamp between 20% and 80%
    setSplitPos(Math.min(80, Math.max(20, newPos)))
  }, [isDragging])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  useEffect(() => {
    const getToken = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setToken(session?.access_token ?? null)
    }
    getToken()
    logger.info('ChatPage mounted')
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
    logger.info(`Tab changed to: ${tab}`)
    if (tab === 'documents' && token) {
      loadDocuments()
    }
  }, [tab, token])

  return (
    <div ref={containerRef} className="flex h-screen">
      {/* Left Side - Resizable */}
      <div className="flex flex-col bg-muted/30" style={{ width: `${splitPos}%` }}>
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between shrink-0">
          <div>
            <h1 className="font-semibold text-lg">kikiKen</h1>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors"
            title="Logout"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation Tabs - Vertical */}
        <div className="flex border-b shrink-0">
          <button
            onClick={() => setTab('chat')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              tab === 'chat' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            Chat
          </button>
          <button
            onClick={() => setTab('documents')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              tab === 'documents' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            Documents
          </button>
        </div>

        {/* Sidebar Content */}
        {tab === 'chat' ? (
          <ConversationList
            conversations={conversations}
            activeId={activeConversationId}
            onSelect={loadMessages}
            onDelete={deleteConversation}
            onRename={renameConversation}
          />
        ) : (
          <div className="flex-1 overflow-y-auto p-4">
            <DocumentUpload token={token} onUploadComplete={loadDocuments} />
          </div>
        )}
      </div>

      {/* Resizable Divider */}
      <div
        className={`w-1 bg-border cursor-col-resize shrink-0 transition-colors ${
          isDragging ? 'bg-primary' : 'hover:bg-primary/50'
        }`}
        onMouseDown={handleMouseDown}
      />

      {/* Right Side - Resizable */}
      <div className="flex flex-col" style={{ width: `${100 - splitPos}%` }}>
        {tab === 'chat' ? (
          <ChatWindow
            currentMessages={currentMessages}
            streamingContent={streamingContent}
            loading={loading}
            onSendMessage={sendMessage}
            onNewChat={createConversation}
          />
        ) : (
          <DocumentsView
            documents={documents}
            loading={docsLoading}
            onDelete={handleDeleteDocument}
          />
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
