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

## Bug Fixes (Post-Module 1)

### Chat API RLS Session Fix
- **Problem**: list/delete messages endpoints returned 404 due to RLS not working
- **Fix**: `list_conversations`, `delete_conversation`, `list_messages` now call `supabase.auth.set_session()` before queries

### Message Display Fix
- **Problem**: Clicking conversation didn't show messages
- **Fix**: `ChatPage` and `ChatWindow` now share state via props instead of each calling `useChat()` independently

### Assistant Message Storage Fix
- **Problem**: Assistant replies weren't stored in database
- **Fix**: Now inserts new assistant message instead of trying to UPDATE user message

### LangSmith Tracing Fix
- **Problem**: LangSmith traces not appearing in dashboard
- **Fix**: `config.py` now sets `os.environ` vars in `Settings.__init__()` before modules load

### Startup Scripts
- Added `start.bat`, `start.sh`, `stop.bat`, `stop.sh` for convenient service management

## Environment Configuration

### `backend/.env`:
```bash
OPENAI_BASE_URL=https://api.minimax.chat/v1
OPENAI_MODEL=MiniMax-M2.7-highspeed
```

## Test Account
- **Email**: test@test.com
- **Password**: kC8u+jyJ*hF66si
- **Supabase URL**: https://oxbxlcpsdkjnoswsilli.supabase.co

## Quick Commands

```bash
# Start both services (recommended: use Git Bash)
./start.sh

# Stop all services
./stop.sh

# Manual start
cd backend && ./venv/Scripts/uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Context Files
- `context/2026-03-20_01-03-40.md` - Previous context
- `context/2026-03-20_02-XX-XX.md` - Current context
