import { useState, useRef, KeyboardEvent } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface Props {
  onSend: (message: string) => void
  loading: boolean
}

const SUGGESTIONS = [
  'What is the remote work policy?',
  'Summarize the onboarding process.',
  'How do I request production access?',
  'What is the equity vesting schedule?',
]

export default function ChatInput({ onSend, loading }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || loading) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Suggestions (shown only when textarea empty) */}
      {!value && (
        <div className="flex flex-wrap gap-2 px-1">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => { setValue(s); textareaRef.current?.focus() }}
              className="px-3 py-1.5 rounded-full text-xs border border-surface-500 text-zinc-400 hover:border-brand-500/40 hover:text-zinc-200 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex items-end gap-3 px-4 py-3 rounded-2xl bg-surface-700 border border-surface-500 focus-within:border-brand-500/40 transition-colors">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => { setValue(e.target.value); handleInput() }}
          onKeyDown={handleKey}
          placeholder="Ask anything about your company docs…"
          rows={1}
          disabled={loading}
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder-zinc-600 outline-none leading-relaxed disabled:opacity-50"
        />
        <button
          onClick={submit}
          disabled={!value.trim() || loading}
          className="shrink-0 w-8 h-8 rounded-xl flex items-center justify-center bg-brand-500 text-white transition-all hover:bg-brand-600 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
        </button>
      </div>
      <p className="text-center text-[11px] text-zinc-600">Enter to send · Shift+Enter for new line</p>
    </div>
  )
}
