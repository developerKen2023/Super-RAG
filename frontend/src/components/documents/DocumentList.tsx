import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { FileText, Trash2, Clock, AlertTriangle, FileSearch, X } from 'lucide-react'
import type { DocumentMetadata } from '@/lib/api'

interface Document {
  id: string
  filename: string
  status: string
  chunk_count: number
  created_at: string
  metadata?: Record<string, unknown>
}

interface DocumentListProps {
  documents: Document[]
  onDelete: (id: string) => void
  loading?: boolean
  selectedIds: Set<string>
  onSelectOne: (id: string, checked: boolean) => void
  onSelectAll: (checked: boolean) => void
  isAllSelected: boolean
  isSomeSelected: boolean
}

interface ConfirmDialogProps {
  open: boolean
  filename: string
  onConfirm: () => void
  onCancel: () => void
}

function ConfirmDialog({ open, filename, onConfirm, onCancel }: ConfirmDialogProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />

      {/* Dialog */}
      <div className="relative bg-background rounded-lg shadow-lg border p-6 w-full max-w-md mx-4">
        <div className="flex items-start gap-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold">Delete Document</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Are you sure you want to delete <span className="font-medium text-foreground">"{filename}"</span>? This action cannot be undone.
            </p>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}

interface MetadataDetailDialogProps {
  open: boolean
  document: Document | null
  onClose: () => void
}

function MetadataDetailDialog({ open, document, onClose }: MetadataDetailDialogProps) {
  if (!open || !document) return null

  const meta = document.metadata as DocumentMetadata | undefined

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined) return 'no record'
    if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : 'no record'
    if (typeof value === 'string') return value || 'no record'
    return String(value)
  }

  const rows = [
    { label: 'Title', value: meta?.title },
    { label: 'Author', value: meta?.author },
    { label: 'Date', value: meta?.date },
    { label: 'Category', value: meta?.category },
    { label: 'Tags', value: meta?.tags },
    { label: 'Summary', value: meta?.summary },
    { label: 'Language', value: meta?.language },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Dialog */}
      <div className="relative bg-background rounded-lg shadow-lg border w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b shrink-0">
          <div className="flex items-center gap-2">
            <FileSearch className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-lg font-semibold">Document Metadata</h3>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <table className="w-full text-sm">
            <tbody>
              {rows.map((row) => (
                <tr key={row.label} className="border-b last:border-b-0">
                  <td className="py-3 pr-4 font-medium text-muted-foreground w-28 shrink-0">
                    {row.label}
                  </td>
                  <td className="py-3 text-foreground break-words">
                    {formatValue(row.value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-muted/30 shrink-0">
          <p className="text-xs text-muted-foreground">
            Document: <span className="font-medium">{document.filename}</span>
          </p>
        </div>
      </div>
    </div>
  )
}

export function DocumentList({
  documents,
  onDelete,
  loading,
  selectedIds,
  onSelectOne,
  onSelectAll,
  isAllSelected,
  isSomeSelected,
}: DocumentListProps) {
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; filename: string } | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

  const getDocMetadata = (doc: Document): DocumentMetadata | undefined => {
    return doc.metadata as DocumentMetadata | undefined
  }
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
      {/* Header with select all */}
      <div className="flex items-center gap-3 px-2">
        <input
          type="checkbox"
          className="h-4 w-4 rounded border-input accent-primary"
          checked={isAllSelected}
          ref={(el) => {
            if (el) el.indeterminate = isSomeSelected && !isAllSelected
          }}
          onChange={(e) => onSelectAll(e.target.checked)}
        />
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          Your Documents ({documents.length})
        </span>
      </div>

      {documents.map((doc) => (
        <div
          key={doc.id}
          className={`flex items-center justify-between p-2 rounded-lg hover:bg-accent transition-colors group ${
            selectedIds.has(doc.id) ? 'bg-accent' : ''
          }`}
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-input accent-primary shrink-0"
              checked={selectedIds.has(doc.id)}
              onChange={(e) => {
                e.stopPropagation()
                onSelectOne(doc.id, e.target.checked)
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <div
              className="min-w-0 flex-1 cursor-pointer"
              onClick={() => setSelectedDoc(doc)}
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                <p className="text-sm font-medium truncate">{doc.filename}</p>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground ml-6">
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
              {(() => {
                const meta = getDocMetadata(doc)
                const tags = meta?.tags || []
                return tags.length > 0 ? (
                  <div className="flex gap-1 mt-1 ml-6">
                    {tags.map(tag => (
                      <span key={tag} className="text-xs bg-muted px-1.5 py-0.5 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : null
              })()}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="shrink-0 text-muted-foreground hover:text-destructive"
            onClick={() => setConfirmDelete({ id: doc.id, filename: doc.filename })}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ))}

      <ConfirmDialog
        open={confirmDelete !== null}
        filename={confirmDelete?.filename || ''}
        onConfirm={() => {
          if (confirmDelete) {
            onDelete(confirmDelete.id)
            setConfirmDelete(null)
          }
        }}
        onCancel={() => setConfirmDelete(null)}
      />

      <MetadataDetailDialog
        open={selectedDoc !== null}
        document={selectedDoc}
        onClose={() => setSelectedDoc(null)}
      />
    </div>
  )
}
