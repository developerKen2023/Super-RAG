import { DocumentList } from './DocumentList'

interface Document {
  id: string
  user_id: string
  filename: string
  file_path: string
  file_size: number
  mime_type: string
  status: string
  chunk_count: number
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

interface DocumentsViewProps {
  documents: Document[]
  loading: boolean
  onDelete: (id: string) => void
}

export function DocumentsView({
  documents,
  loading,
  onDelete,
}: DocumentsViewProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4 bg-muted/30">
        <h2 className="font-semibold text-lg">Your Documents</h2>
        <p className="text-sm text-muted-foreground">
          {documents.length} document{documents.length !== 1 ? 's' : ''}
        </p>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto">
          <DocumentList
            documents={documents}
            onDelete={onDelete}
            loading={loading}
          />
        </div>
      </div>
    </div>
  )
}
