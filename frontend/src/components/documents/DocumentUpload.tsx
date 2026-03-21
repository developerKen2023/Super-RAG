import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Upload } from 'lucide-react'

interface DocumentUploadProps {
  token: string | null
  onUploadComplete?: () => void
}

export function DocumentUpload({ token, onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleUpload = async (file: File) => {
    if (!token) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/documents/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })

      if (!response.ok) throw new Error('Upload failed')
      onUploadComplete?.()
    } catch (error) {
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
        dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-muted-foreground/50'
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <Upload className="mx-auto h-6 w-6 text-muted-foreground mb-2" />
      <p className="text-sm text-muted-foreground mb-2">
        Drag & drop or click to upload
      </p>
      <input
        type="file"
        className="hidden"
        id="file-upload"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleUpload(file)
        }}
      />
      <Button
        variant="outline"
        size="sm"
        onClick={() => document.getElementById('file-upload')?.click()}
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Select File'}
      </Button>
      <p className="text-xs text-muted-foreground mt-2">PDF, TXT, MD</p>
    </div>
  )
}
