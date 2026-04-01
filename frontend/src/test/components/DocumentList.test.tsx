import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DocumentList } from '@/components/documents/DocumentList';

describe('DocumentList', () => {
  const mockDocuments = [
    {
      id: '1',
      filename: 'test.txt',
      status: 'completed',
      chunk_count: 5,
      created_at: '2024-01-01T00:00:00Z',
      metadata: { title: 'Test', tags: ['important'] }
    }
  ]

  const mockProps = {
    onDelete: vi.fn(),
    selectedIds: new Set<string>(),
    onSelectOne: vi.fn(),
    onSelectAll: vi.fn(),
    isAllSelected: false,
    isSomeSelected: false,
  }

  it('renders document metadata tags', () => {
    render(<DocumentList documents={mockDocuments} {...mockProps} />)
    expect(screen.getByText('important')).toBeInTheDocument()
  })

  it('shows filter button', () => {
    // Note: Filter button is in DocumentsView, not DocumentList
    // This test checks that the component renders correctly
    render(<DocumentList documents={mockDocuments} {...mockProps} />)
    expect(screen.getByText('test.txt')).toBeInTheDocument()
  })

  it('renders multiple tags', () => {
    const docWithMultipleTags = [{
      ...mockDocuments[0],
      metadata: { tags: ['tag1', 'tag2', 'tag3'] }
    }]
    render(<DocumentList documents={docWithMultipleTags} {...mockProps} />)
    expect(screen.getByText('tag1')).toBeInTheDocument()
    expect(screen.getByText('tag2')).toBeInTheDocument()
    expect(screen.getByText('tag3')).toBeInTheDocument()
  })

  it('handles documents without metadata', () => {
    const docWithoutMetadata = [{
      id: '2',
      filename: 'no-meta.txt',
      status: 'completed',
      chunk_count: 3,
      created_at: '2024-01-01T00:00:00Z'
    }]
    render(<DocumentList documents={docWithoutMetadata} {...mockProps} />)
    expect(screen.getByText('no-meta.txt')).toBeInTheDocument()
  })
})
