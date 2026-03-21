import { Button } from '@/components/ui/button'
import { FileText, Trash2, Clock } from 'lucide-react'

interface Document {
  id: string
  filename: string
  status: string
  chunk_count: number
  created_at: string
}

interface DocumentListProps {
  documents: Document[]
  onDelete: (id: string) => void
  loading?: boolean
}

export function DocumentList({ documents, onDelete, loading }: DocumentListProps) {
  if (loading) {
    return (
      <div className="text-center text-sm text-muted-foreground py-4">
        Loading...
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center text-sm text-muted-foreground py-4">
        <FileText className="mx-auto h-8 w-8 mb-2 opacity-50" />
        <p>No documents uploaded</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
        Your Documents ({documents.length})
      </p>
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-2 rounded-lg hover:bg-accent transition-colors"
        >
          <div className="flex items-center gap-3 min-w-0">
            <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{doc.filename}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {new Date(doc.created_at).toLocaleDateString()}
                </span>
                <span>•</span>
                <span>{doc.chunk_count} chunks</span>
                <span>•</span>
                <span className={`capitalize ${
                  doc.status === 'completed' ? 'text-green-600' :
                  doc.status === 'failed' ? 'text-red-600' :
                  doc.status === 'processing' ? 'text-yellow-600' : ''
                }`}>{doc.status}</span>
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="shrink-0 text-muted-foreground hover:text-destructive"
            onClick={() => onDelete(doc.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  )
}
