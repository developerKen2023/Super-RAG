import { useState, useCallback, useRef } from 'react'
import { supabase } from '@/lib/supabase'
import { chatApi, createChatStream } from '@/lib/api'

export interface Source {
  filename: string
  content: string
  bm25_rank?: number
  vector_rank?: number
  rrf_score?: number
  similarity?: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  sources?: Source[]
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [currentMessages, setCurrentMessages] = useState<Message[]>([])
  const [streamingContent, setStreamingContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const isSendingRef = useRef(false)

  const loadConversations = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      const convs = await chatApi.listConversations(session.access_token)
      setConversations(convs)
    } catch (err) {
      setError('Failed to load conversations')
    }
  }, [])

  const loadMessages = useCallback(async (conversationId: string) => {
    console.log('[DEBUG] loadMessages called with:', conversationId)
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      const msgs = await chatApi.listMessages(session.access_token, conversationId)
      console.log('[DEBUG] loadMessages got:', msgs.length, 'messages')
      setCurrentMessages(msgs)
      setActiveConversationId(conversationId)
    } catch (err) {
      console.error('[DEBUG] loadMessages error:', err)
      setError('Failed to load messages')
    }
  }, [])

  const sendMessage = useCallback(async (
    content: string,
    ragFilters?: { tag?: string; category?: string }
  ) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    // Prevent double-send
    if (isSendingRef.current) return
    isSendingRef.current = true

    setLoading(true)
    setError(null)
    setStreamingContent('')

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    console.log('[DEBUG] Adding userMessage:', userMessage)
    setCurrentMessages(prev => {
      console.log('[DEBUG] setCurrentMessages (add user):', prev.length, 'messages')
      return [...prev, userMessage]
    })

    let fullContent = ''
    let messageSources: Source[] = []

    try {
      await new Promise<void>((resolve, reject) => {
        const controller = createChatStream(
          session.access_token,
          activeConversationId,
          content,
          'minimax',
          ragFilters,
          (delta: string) => {
            fullContent += delta
            setStreamingContent(fullContent)
          },
          (responseId: string, conversationId?: string) => {
            console.log('[DEBUG] Stream done, responseId:', responseId, 'conversationId:', conversationId)
            const assistantMessage: Message = {
              id: responseId,
              role: 'assistant',
              content: fullContent,
              created_at: new Date().toISOString(),
              sources: messageSources.length > 0 ? messageSources : undefined,
            }
            console.log('[DEBUG] Adding assistant message, keeping user message')
            setCurrentMessages(prev => {
              console.log('[DEBUG] setCurrentMessages (add assistant):', prev.length, 'messages')
              // Keep user message and add assistant message
              return [...prev, assistantMessage]
            })
            setStreamingContent('')

            // If backend returned a new conversation ID, update activeConversationId
            if (conversationId && !activeConversationId) {
              console.log('[DEBUG] Setting activeConversationId to:', conversationId)
              setActiveConversationId(conversationId)
            }

            resolve()
          },
          (err: string) => {
            console.error('[DEBUG] Stream error:', err)
            setError(err)
            reject(new Error(err))
          },
          (sources: Source[]) => {
            console.log('[DEBUG] Received sources:', sources.length)
            messageSources = sources
          }
        )
        abortControllerRef.current = controller
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      console.log('[DEBUG] Finally block, activeConversationId:', activeConversationId)
      setLoading(false)
      if (abortControllerRef.current) abortControllerRef.current.abort()
      // Don't await loadConversations here - let it run async without blocking
      loadConversations()
      isSendingRef.current = false
    }
  }, [activeConversationId, loadConversations])

  const createConversation = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      const conv = await chatApi.createConversation(session.access_token)
      // Reload all conversations to ensure state sync
      const convs = await chatApi.listConversations(session.access_token)
      setConversations(convs)
      setCurrentMessages([])
      setActiveConversationId(conv.id)
      return conv
    } catch (err) {
      setError('Failed to create conversation')
      return null
    }
  }, [])

  const deleteConversation = useCallback(async (conversationId: string) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      await chatApi.deleteConversation(session.access_token, conversationId)
      setConversations(prev => prev.filter(c => c.id !== conversationId))
      if (activeConversationId === conversationId) {
        setActiveConversationId(null)
        setCurrentMessages([])
      }
    } catch (err) {
      setError('Failed to delete conversation')
    }
  }, [activeConversationId])

  const renameConversation = useCallback(async (conversationId: string, title: string) => {
    console.log('renameConversation called', { conversationId, title })
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) {
      console.log('No access token')
      return
    }

    try {
      console.log('Calling API...')
      const updated = await chatApi.updateConversation(session.access_token, conversationId, title)
      console.log('API returned', updated)
      setConversations(prev => prev.map(c => c.id === conversationId ? updated : c))
    } catch (err) {
      console.error('Rename failed', err)
      setError('Failed to rename conversation')
    }
  }, [])

  return {
    conversations,
    activeConversationId,
    currentMessages,
    streamingContent,
    loading,
    error,
    loadConversations,
    loadMessages,
    sendMessage,
    createConversation,
    deleteConversation,
    renameConversation,
  }
}
