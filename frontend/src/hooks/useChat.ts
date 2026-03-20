import { useState, useCallback, useRef } from 'react'
import { supabase } from '@/lib/supabase'
import { chatApi, createChatStream } from '@/lib/api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
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
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      const msgs = await chatApi.listMessages(session.access_token, conversationId)
      setCurrentMessages(msgs)
      setActiveConversationId(conversationId)
    } catch (err) {
      setError('Failed to load messages')
    }
  }, [])

  const sendMessage = useCallback(async (content: string) => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    setLoading(true)
    setError(null)
    setStreamingContent('')

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setCurrentMessages(prev => [...prev, userMessage])

    let fullContent = ''

    try {
      await new Promise<void>((resolve, reject) => {
        const controller = createChatStream(
          session.access_token,
          activeConversationId,
          content,
          (delta) => {
            fullContent += delta
            setStreamingContent(fullContent)
          },
          (responseId) => {
            const assistantMessage: Message = {
              id: responseId,
              role: 'assistant',
              content: fullContent,
              created_at: new Date().toISOString(),
            }
            setCurrentMessages(prev => [...prev.filter(m => m.id !== userMessage.id), assistantMessage])
            setStreamingContent('')
            resolve()
          },
          (err) => {
            setError(err)
            reject(new Error(err))
          }
        )
        abortControllerRef.current = controller
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setLoading(false)
      if (abortControllerRef.current) abortControllerRef.current.abort()
      await loadConversations()
    }
  }, [activeConversationId, loadConversations])

  const createConversation = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return

    try {
      const conv = await chatApi.createConversation(session.access_token)
      setConversations(prev => [conv, ...prev])
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
  }
}
