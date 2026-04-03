import { useEffect, useRef } from 'react'
import { Trash2, BookOpen } from 'lucide-react'
import { useChat } from '../hooks/useChat'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

export default function ChatPage() {
  const { messages, loading, sendMessage, clearMessages } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-surface-600">
        <div>
          <h1 className="font-display text-base font-600 text-white">Ask your knowledge base</h1>
          <p className="text-xs text-zinc-500 mt-0.5">Answers are grounded in your ingested documents</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-2.5 py-1.5 rounded-lg hover:bg-surface-700"
          >
            <Trash2 size={13} />
            Clear chat
          </button>
        )}
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-6">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map(msg => <ChatMessage key={msg.id} message={msg} />)
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3">
            <div className="shrink-0 w-8 h-8 rounded-lg bg-surface-600 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-surface-700 border border-surface-500 text-sm text-zinc-500 italic">
              Searching knowledge base…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 px-6 pb-6">
        <ChatInput onSend={sendMessage} loading={loading} />
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center py-16 gap-4">
      <div className="w-14 h-14 rounded-2xl bg-surface-700 border border-surface-500 flex items-center justify-center">
        <BookOpen size={22} className="text-brand-500" />
      </div>
      <div>
        <p className="font-display text-lg text-white font-600">Ready to answer</p>
        <p className="text-sm text-zinc-500 mt-1 max-w-xs">
          Ask any question about your company's policies, processes, or documentation.
        </p>
      </div>
    </div>
  )
}
