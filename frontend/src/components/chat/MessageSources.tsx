interface Source {
  filename: string
  content: string
  bm25_rank?: number
  vector_rank?: number
  rrf_score?: number
  similarity?: number
}

interface MessageSourcesProps {
  sources?: Source[]
}

export function MessageSources({ sources }: MessageSourcesProps) {
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-2 text-xs border-t border-border pt-2">
      <p className="font-medium text-muted-foreground mb-1">Sources:</p>
      <ul className="space-y-1">
        {sources.map((source, i) => (
          <li key={i} className="flex flex-col gap-0.5 text-muted-foreground">
            <div className="flex items-center gap-1">
              <span className="text-primary font-medium">[{i + 1}]</span>
              <span className="font-medium">{source.filename}</span>
              {source.rrf_score !== undefined && (
                <span className="text-primary">(RRF: {source.rrf_score.toFixed(3)})</span>
              )}
              {source.similarity !== undefined && (
                <span className="text-primary">(Sim: {source.similarity.toFixed(3)})</span>
              )}
            </div>
            <div className="text-xs pl-4 text-muted-foreground/70">
              {source.bm25_rank !== undefined && `BM25: ${source.bm25_rank + 1}`}
              {source.bm25_rank !== undefined && source.vector_rank !== undefined && ' | '}
              {source.vector_rank !== undefined && `Vec: ${source.vector_rank + 1}`}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
