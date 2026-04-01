import { useState, useRef } from 'react'
import { flushSync } from 'react-dom'
import { Button } from '@/components/ui/button'
import { Upload, AlertTriangle, X, CheckCircle, FileX, Files, Clock } from 'lucide-react'

interface DocumentUploadProps {
  token: string | null
  onUploadComplete?: () => void
}

interface UploadItem {
  id: string
  filename: string
  status: 'pending' | 'uploading' | 'completed' | 'failed' | 'duplicate'
  progress: number
  error?: string
  duplicateOf?: string
}

const MAX_FILE_SIZE_MB = 5
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

export function DocumentUpload({ token, onUploadComplete }: DocumentUploadProps) {
  const [dragOver, setDragOver] = useState(false)
  const [uploadQueue, setUploadQueue] = useState<UploadItem[]>([])
  const [isUploading, setIsUploading] = useState(false)

  // Store files by item id for upload
  const pendingFilesRef = useRef<Map<string, File>>(new Map())
  const currentUploadIdRef = useRef<string | null>(null)
  const uploadQueueRef = useRef<UploadItem[]>([])
  const isUploadingRef = useRef(false)

  // Keep refs in sync with state
  uploadQueueRef.current = uploadQueue

  // Upload a single file with progress tracking
  const uploadFile = (itemId: string, file: File): Promise<void> => {
    return new Promise((resolve) => {
      const xhr = new XMLHttpRequest()
      const formData = new FormData()
      formData.append('file', file)

      xhr.addEventListener('load', () => {
        try {
          const result = JSON.parse(xhr.responseText)

          setUploadQueue(prev => {
            const updated = prev.map(i => i.id === itemId ? { ...i, progress: 100 } : i)

            if (result.status === 'duplicate') {
              const final = updated.map(i => i.id === itemId
                ? { ...i, status: 'duplicate' as const, duplicateOf: result.duplicate_of }
                : i
              )
              uploadQueueRef.current = final
              return final
            } else if (xhr.status >= 200 && xhr.status < 300) {
              const final = updated.map(i => i.id === itemId ? { ...i, status: 'completed' as const } : i)
              uploadQueueRef.current = final
              return final
            } else {
              const final = updated.map(i => i.id === itemId
                ? { ...i, status: 'failed' as const, error: result.detail || 'Upload failed' }
                : i
              )
              uploadQueueRef.current = final
              return final
            }
          })
        } catch {
          setUploadQueue(prev => {
            const updated = prev.map(i => i.id === itemId
              ? { ...i, status: 'failed' as const, error: 'Invalid response' }
              : i
            )
            uploadQueueRef.current = updated
            return updated
          })
        }

        currentUploadIdRef.current = null
        onUploadComplete?.()
        startNextUpload()
        resolve()
      })

      xhr.addEventListener('error', () => {
        setUploadQueue(prev => {
          const updated = prev.map(i => i.id === itemId
            ? { ...i, status: 'failed' as const, error: 'Network error' }
            : i
          )
          uploadQueueRef.current = updated
          return updated
        })
        currentUploadIdRef.current = null
        onUploadComplete?.()
        startNextUpload()
        resolve()
      })

      xhr.addEventListener('abort', () => {
        setUploadQueue(prev => {
          const updated = prev.map(i => i.id === itemId
            ? { ...i, status: 'failed' as const, error: 'Upload cancelled' }
            : i
          )
          uploadQueueRef.current = updated
          return updated
        })
        currentUploadIdRef.current = null
        startNextUpload()
        resolve()
      })

      // Progress tracking - cap at 99% until complete
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percent = Math.min(99, Math.round((e.loaded / e.total) * 100))
          setUploadQueue(prev => {
            const updated = prev.map(i => i.id === itemId ? { ...i, progress: percent } : i)
            uploadQueueRef.current = updated
            return updated
          })
        }
      })

      xhr.open('POST', `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/documents/upload`)
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(formData)
    })
  }

  // Start next pending upload
  const startNextUpload = () => {
    if (currentUploadIdRef.current !== null) return
    if (isUploadingRef.current === false) return

    const queue = uploadQueueRef.current
    const nextItem = queue.find(item => item.status === 'pending')
    if (!nextItem) {
      const stillUploading = queue.some(
        item => item.status === 'uploading' || item.status === 'pending'
      )
      if (!stillUploading) {
        isUploadingRef.current = false
        setIsUploading(false)
      }
      return
    }

    const file = pendingFilesRef.current.get(nextItem.id)
    if (!file) {
      setUploadQueue(prev => {
        const updated = prev.map(i => i.id === nextItem.id
          ? { ...i, status: 'failed' as const, error: 'File not found' }
          : i
        )
        uploadQueueRef.current = updated
        return updated
      })
      startNextUpload()
      return
    }

    currentUploadIdRef.current = nextItem.id
    setUploadQueue(prev => {
      const updated = prev.map(i => i.id === nextItem.id
        ? { ...i, status: 'uploading' as const, progress: 0 }
        : i
      )
      uploadQueueRef.current = updated
      return updated
    })

    uploadFile(nextItem.id, file)
  }

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0 || !token) return

    const newItems: UploadItem[] = []

    Array.from(files).forEach((file, index) => {
      const id = `${Date.now()}-${index}-${file.name}`

      if (file.size > MAX_FILE_SIZE_BYTES) {
        newItems.push({
          id,
          filename: file.name,
          status: 'failed',
          progress: 0,
          error: `File size exceeds ${MAX_FILE_SIZE_MB}MB limit`
        })
      } else {
        pendingFilesRef.current.set(id, file)
        newItems.push({
          id,
          filename: file.name,
          status: 'pending',
          progress: 0
        })
      }
    })

    isUploadingRef.current = true
    flushSync(() => {
      setIsUploading(true)
    })
    flushSync(() => {
      setUploadQueue(prev => {
        const updated = [...prev, ...newItems]
        uploadQueueRef.current = updated
        return updated
      })
    })

    startNextUpload()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const removeItem = (id: string) => {
    pendingFilesRef.current.delete(id)
    if (currentUploadIdRef.current === id) {
      currentUploadIdRef.current = null
    }
    setUploadQueue(prev => {
      const updated = prev.filter(i => i.id !== id)
      uploadQueueRef.current = updated
      return updated
    })
  }

  const clearCompleted = () => {
    setUploadQueue(prev => {
      const updated = prev.filter(item => item.status !== 'completed')
      uploadQueueRef.current = updated
      return updated
    })
  }

  const getStatusIcon = (status: UploadItem['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600 shrink-0" />
      case 'failed':
        return <FileX className="h-4 w-4 text-red-600 shrink-0" />
      case 'duplicate':
        return <AlertTriangle className="h-4 w-4 text-yellow-600 shrink-0" />
      case 'uploading':
        return <Files className="h-4 w-4 text-blue-600 animate-pulse shrink-0" />
      default:
        return <Clock className="h-4 w-4 text-gray-400 shrink-0" />
    }
  }

  const getStatusText = (status: UploadItem['status']) => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      case 'duplicate':
        return 'Duplicate'
      case 'uploading':
        return 'Uploading'
      default:
        return 'Pending'
    }
  }

  const completedCount = uploadQueue.filter(item => item.status === 'completed').length
  const failedCount = uploadQueue.filter(item => item.status === 'failed').length
  const duplicateCount = uploadQueue.filter(item => item.status === 'duplicate').length
  const pendingCount = uploadQueue.filter(item => item.status === 'pending').length
  const uploadingCount = uploadQueue.filter(item => item.status === 'uploading').length

  return (
    <div className="space-y-4">
      {/* Upload area */}
      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
          dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-muted-foreground/50'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <Upload className={`mx-auto h-6 w-6 mb-2 ${isUploading ? 'text-gray-400' : 'text-muted-foreground'}`} />
        <p className={`text-sm mb-2 ${isUploading ? 'text-gray-500' : 'text-muted-foreground'}`}>
          {isUploading ? 'Uploading...' : 'Drag & drop or click to upload'}
        </p>
        <input
          type="file"
          className="hidden"
          id="file-upload"
          multiple
          disabled={isUploading}
          onChange={(e) => handleFiles(e.target.files)}
        />
        <Button
          variant="outline"
          size="sm"
          disabled={isUploading}
          onClick={() => document.getElementById('file-upload')?.click()}
        >
          <Files className="h-4 w-4 mr-1" />
          {isUploading ? 'Uploading...' : 'Select Files'}
        </Button>
        <p className="text-xs text-muted-foreground mt-2">
          PDF, DOCX, HTML, MD, TXT (max {MAX_FILE_SIZE_MB}MB each)
        </p>
      </div>

      {/* Upload queue */}
      {uploadQueue.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">
              Upload Queue ({uploadQueue.length})
              {uploadingCount > 0 && <span className="text-blue-600 ml-1">({uploadingCount} uploading)</span>}
              {pendingCount > 0 && <span className="text-gray-500 ml-1">({pendingCount} pending)</span>}
            </h4>
            {completedCount > 0 && (
              <Button variant="ghost" size="sm" onClick={clearCompleted}>
                Clear completed
              </Button>
            )}
          </div>

          {/* Summary stats */}
          {(completedCount > 0 || failedCount > 0 || duplicateCount > 0) && (
            <div className="flex gap-3 text-xs">
              {completedCount > 0 && (
                <span className="text-green-600">{completedCount} completed</span>
              )}
              {failedCount > 0 && (
                <span className="text-red-600">{failedCount} failed</span>
              )}
              {duplicateCount > 0 && (
                <span className="text-yellow-600">{duplicateCount} duplicate</span>
              )}
            </div>
          )}

          {/* File list */}
          <div className="max-h-60 overflow-y-auto space-y-1">
            {uploadQueue.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-2 bg-muted/50 rounded text-sm"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  {getStatusIcon(item.status)}
                  <span className="truncate">{item.filename}</span>
                  {item.status === 'uploading' && (
                    <span className="text-xs text-blue-600 shrink-0">{item.progress}%</span>
                  )}
                </div>
                {/* Progress bar for uploading files */}
                {item.status === 'uploading' && (
                  <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden shrink-0 mx-2">
                    <div
                      className="h-full bg-blue-500 transition-all duration-200"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                )}
                <div className="flex items-center gap-2 shrink-0">
                  {item.status === 'failed' && item.error && (
                    <span className="text-xs text-red-600 truncate max-w-32">{item.error}</span>
                  )}
                  {item.status === 'duplicate' && (
                    <span className="text-xs text-yellow-600">Duplicate</span>
                  )}
                  <span className="text-xs text-gray-500">{getStatusText(item.status)}</span>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
