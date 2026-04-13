import { useState, useEffect, useCallback } from 'react'
import { BarChart2, Database, FileText, Zap, RefreshCw, AlertCircle } from 'lucide-react'
import { getStatus, StatusResponse } from '../lib/api'

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  sub?: string
  accent?: boolean
}

function StatCard({ icon, label, value, sub, accent }: StatCardProps) {
  return (
    <div className={`flex items-start gap-3 px-4 py-4 rounded-xl border ${
      accent
        ? 'bg-brand-500/5 border-brand-500/20'
        : 'bg-surface-800 border-surface-600'
    }`}>
      <div className={`mt-0.5 w-8 h-8 rounded-lg flex items-center justify-center ${
        accent ? 'bg-brand-500/10 text-brand-500' : 'bg-surface-600 text-zinc-400'
      }`}>
        {icon}
      </div>
      <div>
        <p className="text-xs text-zinc-500">{label}</p>
        <p className={`text-xl font-display font-700 mt-0.5 ${accent ? 'text-brand-500' : 'text-white'}`}>
          {value}
        </p>
        {sub && <p className="text-xs text-zinc-600 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function StatsPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null)

  const fetchStatus = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const s = await getStatus()
      setStatus(s)
      setLastRefreshed(new Date())
    } catch (e) {
      setError('Could not reach backend. Is the server running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchStatus() }, [fetchStatus])

  const avgChunksPerDoc =
    status && status.sources.length > 0
      ? Math.round(status.chunk_count / status.sources.length)
      : 0

  return (
    <div className="h-full overflow-y-auto px-6 py-6 flex flex-col gap-6 max-w-3xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-base font-600 text-white">Knowledge Base Stats</h1>
          <p className="text-xs text-zinc-500 mt-0.5">
            {lastRefreshed
              ? `Last updated: ${lastRefreshed.toLocaleTimeString()}`
              : 'Connecting…'}
          </p>
        </div>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-3 py-1.5 rounded-lg hover:bg-surface-700 disabled:opacity-40"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Stat grid */}
      {!error && (
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            icon={<Database size={15} />}
            label="Total Chunks Indexed"
            value={loading ? '—' : (status?.chunk_count.toLocaleString() ?? '0')}
            sub="Semantic units in vector store"
            accent
          />
          <StatCard
            icon={<FileText size={15} />}
            label="Documents Ingested"
            value={loading ? '—' : (status?.sources.length ?? 0)}
            sub="Unique source files"
          />
          <StatCard
            icon={<Zap size={15} />}
            label="Avg Chunks / Doc"
            value={loading ? '—' : avgChunksPerDoc}
            sub="Based on current ingestion"
          />
          <StatCard
            icon={<BarChart2 size={15} />}
            label="Embedding Model"
            value="MiniLM-L6"
            sub="all-MiniLM-L6-v2 · 384 dims"
          />
        </div>
      )}

      {/* Source list */}
      {status && status.sources.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-1">
            Indexed Sources ({status.sources.length})
          </p>
          <div className="flex flex-col gap-1.5">
            {status.sources.map((src) => {
              const ext = src.split('.').pop()?.toUpperCase() ?? 'FILE'
              const extColors: Record<string, string> = {
                PDF: 'text-red-400 bg-red-500/10',
                MD: 'text-blue-400 bg-blue-500/10',
                MARKDOWN: 'text-blue-400 bg-blue-500/10',
                DOCX: 'text-indigo-400 bg-indigo-500/10',
                TXT: 'text-zinc-400 bg-zinc-500/10',
              }
              const colorClass = extColors[ext] ?? 'text-zinc-400 bg-zinc-500/10'
              return (
                <div
                  key={src}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-surface-800 border border-surface-600"
                >
                  <span className={`text-[10px] font-mono font-600 px-1.5 py-0.5 rounded ${colorClass}`}>
                    {ext}
                  </span>
                  <span className="text-sm font-mono text-zinc-300 truncate flex-1">{src}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* RAG config reference */}
      <div className="flex flex-col gap-2">
        <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-1">
          RAG Configuration
        </p>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ['LLM', 'Gemma 4 (Ollama)'],
            ['Embeddings', 'all-MiniLM-L6-v2'],
            ['Vector DB', 'ChromaDB (local)'],
            ['Similarity', 'Cosine'],
            ['Chunk Size', '500 tokens'],
            ['Chunk Overlap', '50 tokens'],
            ['Top-K Retrieval', '5 chunks'],
            ['Orchestration', 'LangChain'],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between px-3 py-2 rounded-lg bg-surface-800 border border-surface-600">
              <span className="text-zinc-500">{k}</span>
              <span className="text-zinc-300 font-mono">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}