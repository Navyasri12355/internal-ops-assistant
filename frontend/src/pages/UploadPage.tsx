import { useState, useEffect, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, CheckCircle, XCircle, FileText, Loader2, Database } from 'lucide-react'
import { uploadDocument, getStatus, StatusResponse } from '../lib/api'
import clsx from 'clsx'

interface FileStatus {
  file: File
  state: 'pending' | 'uploading' | 'done' | 'error'
  message?: string
}

export default function UploadPage() {
  const [files, setFiles] = useState<FileStatus[]>([])
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [loadingStatus, setLoadingStatus] = useState(true)

  const fetchStatus = useCallback(async () => {
    try {
      const s = await getStatus()
      setStatus(s)
    } catch {
      // backend may not be running in dev
    } finally {
      setLoadingStatus(false)
    }
  }, [])

  useEffect(() => { fetchStatus() }, [fetchStatus])

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles: FileStatus[] = accepted.map(f => ({ file: f, state: 'pending' }))
    setFiles(prev => [...prev, ...newFiles])
    // auto-upload on drop
    newFiles.forEach(fs => processUpload(fs.file))
  }, [])

  const processUpload = async (file: File) => {
    setFiles(prev => prev.map(f => f.file === file ? { ...f, state: 'uploading' } : f))
    try {
      const res = await uploadDocument(file)
      setFiles(prev => prev.map(f => f.file === file ? { ...f, state: 'done', message: res.message } : f))
      fetchStatus()
    } catch (err) {
      setFiles(prev => prev.map(f =>
        f.file === file ? { ...f, state: 'error', message: err instanceof Error ? err.message : 'Upload failed' } : f
      ))
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/markdown': ['.md', '.markdown'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
  })

  return (
    <div className="h-full overflow-y-auto px-6 py-6 flex flex-col gap-6 max-w-2xl mx-auto w-full">
      <div>
        <h1 className="font-display text-base font-600 text-white">Document Library</h1>
        <p className="text-xs text-zinc-500 mt-0.5">Upload PDFs, Markdown, DOCX, or TXT files to your knowledge base</p>
      </div>

      {/* Status card */}
      <div className="flex items-center gap-4 px-4 py-3 rounded-xl bg-surface-800 border border-surface-600">
        <div className="w-9 h-9 rounded-lg bg-brand-500/10 flex items-center justify-center">
          <Database size={16} className="text-brand-500" />
        </div>
        <div className="flex-1">
          {loadingStatus ? (
            <p className="text-sm text-zinc-500">Connecting to vector store…</p>
          ) : status ? (
            <>
              <p className="text-sm text-white font-medium">{status.chunk_count.toLocaleString()} chunks indexed</p>
              <p className="text-xs text-zinc-500">{status.sources.length} document{status.sources.length !== 1 ? 's' : ''} in knowledge base</p>
            </>
          ) : (
            <p className="text-sm text-red-400">Could not reach backend</p>
          )}
        </div>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'flex flex-col items-center justify-center gap-3 px-6 py-12 rounded-2xl border-2 border-dashed cursor-pointer transition-all',
          isDragActive
            ? 'border-brand-500 bg-brand-500/5'
            : 'border-surface-500 bg-surface-800 hover:border-surface-400 hover:bg-surface-700'
        )}
      >
        <input {...getInputProps()} />
        <div className="w-12 h-12 rounded-xl bg-surface-600 flex items-center justify-center">
          <Upload size={20} className={isDragActive ? 'text-brand-500' : 'text-zinc-400'} />
        </div>
        <div className="text-center">
          <p className="text-sm text-zinc-300">
            {isDragActive ? 'Drop to upload' : 'Drag files here or click to browse'}
          </p>
          <p className="text-xs text-zinc-600 mt-1">PDF · Markdown · DOCX · TXT</p>
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-1">This session</p>
          {files.map((fs, i) => (
            <div key={i} className="flex items-start gap-3 px-4 py-3 rounded-xl bg-surface-800 border border-surface-600">
              <FileText size={15} className="shrink-0 mt-0.5 text-zinc-500" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-zinc-200 truncate">{fs.file.name}</p>
                {fs.message && (
                  <p className={clsx('text-xs mt-0.5', fs.state === 'error' ? 'text-red-400' : 'text-zinc-500')}>
                    {fs.message}
                  </p>
                )}
              </div>
              <div className="shrink-0">
                {fs.state === 'pending' && <div className="w-4 h-4 rounded-full bg-zinc-600" />}
                {fs.state === 'uploading' && <Loader2 size={16} className="text-brand-500 animate-spin" />}
                {fs.state === 'done' && <CheckCircle size={16} className="text-brand-500" />}
                {fs.state === 'error' && <XCircle size={16} className="text-red-400" />}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Existing sources */}
      {status && status.sources.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider px-1">Indexed sources</p>
          {status.sources.map((src) => (
            <div key={src} className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-surface-800 border border-surface-600">
              <FileText size={14} className="text-brand-500/60 shrink-0" />
              <span className="text-sm font-mono text-zinc-300 truncate">{src}</span>
              <CheckCircle size={14} className="text-brand-500 shrink-0 ml-auto" />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
