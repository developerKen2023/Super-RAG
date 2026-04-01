import { useState, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { DocumentList } from './DocumentList'
import { Filter, X, ChevronLeft, ChevronRight, Trash2, AlertTriangle } from 'lucide-react'
import type { DocumentMetadata } from '@/lib/api'

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

const PAGE_SIZE = 20

interface BatchConfirmDialogProps {
  open: boolean
  count: number
  onConfirm: () => void
  onCancel: () => void
}

function BatchConfirmDialog({ open, count, onConfirm, onCancel }: BatchConfirmDialogProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-background rounded-lg shadow-lg border p-6 w-full max-w-md mx-4">
        <div className="flex items-start gap-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold">Delete Documents</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Are you sure you want to delete <span className="font-medium text-foreground">{count} document{count !== 1 ? 's' : ''}</span>? This action cannot be undone.
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

export function DocumentsView({
  documents,
  loading,
  onDelete,
}: DocumentsViewProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set())
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [showBatchConfirm, setShowBatchConfirm] = useState(false)

  // Compute tag counts
  const { availableTags, tagCounts } = useMemo(() => {
    const tags = new Set<string>()
    const counts: Record<string, number> = {}
    documents.forEach(doc => {
      const meta = doc.metadata as unknown as DocumentMetadata | undefined
      meta?.tags?.forEach(tag => {
        tags.add(tag)
        counts[tag] = (counts[tag] || 0) + 1
      })
    })
    return {
      availableTags: Array.from(tags).sort(),
      tagCounts: counts
    }
  }, [documents])

  // Filter documents based on selected tags and category
  const filteredDocuments = useMemo(() => {
    return documents.filter(doc => {
      const meta = doc.metadata as unknown as DocumentMetadata | undefined
      const tags = meta?.tags || []
      const category = meta?.category

      // Filter by selected tags (OR logic - document matches if it has ANY selected tag)
      if (selectedTags.size > 0 && !Array.from(selectedTags).some(tag => tags.includes(tag))) {
        return false
      }

      // Filter by category
      if (selectedCategory && category !== selectedCategory) {
        return false
      }

      return true
    })
  }, [documents, selectedTags, selectedCategory])

  // Paginate filtered documents
  const totalPages = Math.ceil(filteredDocuments.length / PAGE_SIZE)
  const paginatedDocuments = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE
    return filteredDocuments.slice(start, start + PAGE_SIZE)
  }, [filteredDocuments, page])

  // Reset page when filters change
  const handleTagToggle = (tag: string) => {
    setPage(1)
    setSelectedTags(prev => {
      const next = new Set(prev)
      if (next.has(tag)) {
        next.delete(tag)
      } else {
        next.add(tag)
      }
      return next
    })
  }

  const handleCategoryToggle = (category: string) => {
    setPage(1)
    setSelectedCategory(prev => prev === category ? null : category)
  }

  const handleClearFilters = () => {
    setSelectedTags(new Set())
    setSelectedCategory(null)
    setPage(1)
    setShowFilters(false)
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(paginatedDocuments.map(doc => doc.id)))
    } else {
      setSelectedIds(new Set())
    }
  }

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (checked) {
        next.add(id)
      } else {
        next.delete(id)
      }
      return next
    })
  }

  const handleBatchDelete = () => {
    // Delete each selected document
    selectedIds.forEach(id => onDelete(id))
    setSelectedIds(new Set())
    setShowBatchConfirm(false)
  }

  const isAllSelected = paginatedDocuments.length > 0 && paginatedDocuments.every(doc => selectedIds.has(doc.id))
  const isSomeSelected = paginatedDocuments.some(doc => selectedIds.has(doc.id))

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4 bg-muted/30 flex items-center justify-between shrink-0">
        <div>
          <h2 className="font-semibold text-lg">Your Documents</h2>
          <p className="text-sm text-muted-foreground">
            {filteredDocuments.length} document{filteredDocuments.length !== 1 ? 's' : ''}
            {(selectedTags.size > 0 || selectedCategory) && ' (filtered)'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {selectedIds.size > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setShowBatchConfirm(true)}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Delete ({selectedIds.size})
            </Button>
          )}
          <Button
            variant={showFilters ? "default" : "outline"}
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-1" />
            Filter
          </Button>
        </div>
      </div>

      {showFilters && (
        <div className="border-b p-4 bg-muted/20 shrink-0">
          {/* Selected filters display */}
          {(selectedTags.size > 0 || selectedCategory) && (
            <div className="flex flex-wrap gap-2 mb-3 items-center">
              <span className="text-xs text-muted-foreground">Active filters:</span>
              {Array.from(selectedTags).map(tag => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 text-xs bg-primary text-primary-foreground px-2 py-1 rounded"
                >
                  {tag}
                  <X
                    className="h-3 w-3 cursor-pointer"
                    onClick={() => handleTagToggle(tag)}
                  />
                </span>
              ))}
              {selectedCategory && (
                <span
                  className="inline-flex items-center gap-1 text-xs bg-primary text-primary-foreground px-2 py-1 rounded"
                >
                  {selectedCategory}
                  <X
                    className="h-3 w-3 cursor-pointer"
                    onClick={() => handleCategoryToggle(selectedCategory)}
                  />
                </span>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearFilters}
                className="text-xs h-6 px-2"
              >
                Clear all
              </Button>
            </div>
          )}

          {/* Tag Cloud */}
          <div className="mb-3">
            <p className="text-xs text-muted-foreground mb-2">Tags ({availableTags.length})</p>
            <div className="flex flex-wrap gap-2">
              {availableTags.map(tag => (
                <button
                  key={tag}
                  onClick={() => handleTagToggle(tag)}
                  className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded border transition-colors ${
                    selectedTags.has(tag)
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background border-border hover:bg-accent'
                  }`}
                >
                  {tag}
                  <span className={`text-[10px] ${selectedTags.has(tag) ? 'opacity-80' : 'text-muted-foreground'}`}>
                    {tagCounts[tag]}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto">
          <DocumentList
            documents={paginatedDocuments}
            onDelete={onDelete}
            loading={loading}
            selectedIds={selectedIds}
            onSelectOne={handleSelectOne}
            onSelectAll={handleSelectAll}
            isAllSelected={isAllSelected}
            isSomeSelected={isSomeSelected}
          />
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="border-t p-3 bg-muted/30 flex items-center justify-between shrink-0">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <BatchConfirmDialog
        open={showBatchConfirm}
        count={selectedIds.size}
        onConfirm={handleBatchDelete}
        onCancel={() => setShowBatchConfirm(false)}
      />
    </div>
  )
}
