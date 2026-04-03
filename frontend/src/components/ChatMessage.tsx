import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { ChevronDown, ChevronUp, FileText, User, Bot } from 'lucide-react'
import { Message } from '../hooks/useChat'
import clsx from 'clsx'

interface Props {
  message: Message
}

export default function ChatMessage({ message }: Props) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex gap-3', isUser && 'flex-row-reverse')}>
      {/* Avatar */}
      <div className={clsx(
        'shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5',
        isUser ? 'bg-brand-500/20 text-brand-500' : 'bg-surface-600 text-zinc-400'
      )}>
        {isUser ? <User size={15} /> : <Bot size={15} />}
      </div>

      {/* Bubble */}
      <div className={clsx('max-w-[78%] flex flex-col gap-2', isUser && 'items-end')}>
        <div className={clsx(
          'px-4 py-3 rounded-2xl text-sm leading-relaxed',
          isUser
            ? 'bg-brand-500/15 border border-brand-500/20 text-zinc-100 rounded-tr-sm'
            : message.error
              ? 'bg-red-500/10 border border-red-500/20 text-red-300 rounded-tl-sm'
              : 'bg-surface-700 border border-surface-500 text-zinc-200 rounded-tl-sm'
        )}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose-answer">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources toggle */}
        {message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setShowSources(v => !v)}
              className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              <FileText size={12} />
              {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
              {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {showSources && (
              <div className="mt-2 flex flex-col gap-2">
                {message.sources.map((src, i) => (
                  <div
                    key={i}
                    className="px-3 py-2.5 rounded-lg bg-surface-800 border border-surface-600 text-xs"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-mono text-brand-500 font-medium">{src.source}</span>
                      <div className="flex items-center gap-2 text-zinc-500">
                        <span>p.{src.page}</span>
                        <span className="px-1.5 py-0.5 rounded bg-surface-600 font-mono">
                          {(src.score * 100).toFixed(0)}% match
                        </span>
                      </div>
                    </div>
                    <p className="text-zinc-400 leading-relaxed line-clamp-3">{src.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <span className="text-[11px] text-zinc-600 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}
