import { useState, useCallback } from 'react'
import { queryKnowledge, QueryResponse } from '../lib/api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: QueryResponse['sources']
  error?: boolean
  timestamp: Date
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const sendMessage = useCallback(async (question: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const data = await queryKnowledge(question)
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: err instanceof Error ? err.message : 'Something went wrong.',
        error: true,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }, [])

  const clearMessages = useCallback(() => setMessages([]), [])

  return { messages, loading, sendMessage, clearMessages }
}
