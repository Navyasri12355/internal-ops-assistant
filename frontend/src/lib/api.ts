const BASE_URL = '/api'

export interface ChunkResult {
  content: string
  source: string
  page: number
  score: number
}

export interface QueryResponse {
  answer: string
  sources: ChunkResult[]
  question: string
}

export interface StatusResponse {
  chunk_count: number
  sources: string[]
}

export async function queryKnowledge(question: string, topK = 5): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Query failed: ${res.status}`)
  }
  return res.json()
}

export async function uploadDocument(file: File): Promise<{ message: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Upload failed: ${res.status}`)
  }
  return res.json()
}

export async function getStatus(): Promise<StatusResponse> {
  const res = await fetch(`${BASE_URL}/status`)
  if (!res.ok) throw new Error('Failed to fetch status')
  return res.json()
}
