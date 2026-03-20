# Progress

Track your through the masterclass. Update this file as you complete modules - Claude Code reads this to understand where you are in the project.

## Convention
- `[ ]` = Not started
- `[-]` = In progress
- `[x]` = Completed

## Modules

### Module 1: App Shell + Observability
- [x] Project structure setup (backend + frontend)
- [x] Database schema with RLS (init_db.sql executed in Supabase)
- [x] Backend auth endpoints (signup, login, logout, me)
- [x] Chat Completions API integration (MiniMax-compatible)
- [x] Chat UI with SSE streaming
- [x] LangSmith tracing
- [x] Backend dependency installation (venv + pip install)
- [x] Frontend npm install
- [x] Backend build verification (import test passed)
- [x] Frontend build verification (npm run build passed)
- [x] Backend E2E testing (auth + chat + RLS working)
- [x] Frontend E2E testing (login → chat → verify SSE streaming)

### Module 2: BYO Retrieval + Memory
- [ ] Ingestion UI and processing
- [ ] pgvector setup
- [ ] Chat Completions API (OpenRouter)
- [ ] Chat history storage

### Module 3: Record Manager
- [ ] Content hashing
- [ ] Deduplication

### Module 4: Metadata Extraction
- [ ] LLM metadata extraction
- [ ] Filtered retrieval

### Module 5: Multi-Format Support
- [ ] PDF/DOCX/HTML/Markdown via Docling
- [ ] Cascade deletes

### Module 6: Hybrid Search & Reranking
- [ ] Keyword + vector search
- [ ] RRF combination
- [ ] Reranking

### Module 7: Additional Tools
- [ ] Text-to-SQL tool
- [ ] Web search fallback

### Module 8: Sub-Agents
- [ ] Isolated context
- [ ] Document analysis delegation

## Recent Bug Fixes

### Frontend: SSE streaming via fetch instead of EventSource
- **Problem**: EventSource only supports GET requests, but `/api/chat/stream` is POST
- **Files changed**:
  - `frontend/src/lib/api.ts`: `createChatStream` now uses `fetch` + `ReadableStream` instead of `EventSource`
  - `frontend/src/hooks/useChat.ts`: ref type changed from `EventSource` to `AbortController`

### Backend: RLS session not set in stream_chat endpoint
- **Problem**: 500 error "new row violates row-level security policy for table 'conversations'"
- **Files changed**:
  - `backend/app/api/chat.py`: `stream_chat` now uses `get_authenticated_supabase` instead of `get_supabase` to properly set session for RLS

### Backend: Supabase client timeout configuration
- **Problem**: Backend hangs when Supabase is slow/unreachable
- **Files changed**:
  - `backend/app/supabase.py`: Added `SyncClientOptions` with `postgrest_client_timeout=10`

## MiniMax Configuration

Current `backend/.env` settings:
```bash
OPENAI_BASE_URL=https://api.minimax.chat/v1
OPENAI_MODEL=MiniMax-M2.7-highspeed
OPENAI_API_KEY=your-minimax-api-key
```

## Test Account
- **Email**: test@test.com
- **Password**: kC8u+jyJ*hF66si
- **Supabase URL**: https://oxbxlcpsdkjnoswsilli.supabase.co

## Quick Commands

```bash
# Backend
cd backend
./venv/Scripts/uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

## Context Files

- `context/2026-03-20_01-03-40.md` - Previous project context snapshot
- `context/2026-03-20_02-XX-XX.md` - Current project context (this file after update)
