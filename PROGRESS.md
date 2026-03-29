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
- [x] Multi-LLM Provider Abstraction (MiniMax + Ollama)
- [x] pgvector setup (migrations created)
- [x] MiniMax Embedding Service
- [x] Document API (upload, list, delete)
- [x] Ingestion Pipeline (chunking + embedding + storage)
- [x] Document Upload UI (drag & drop)
- [x] Document List UI
- [x] Chat with Documents tabs (frontend)
- [x] Provider selection in chat API
- [x] RLS policies for documents and document_chunks tables
- [x] RAG Retrieval Service (vector search + context injection)
- [x] RAG-enhanced chat API (retrieves relevant chunks before answering)

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

---

## Bug Fixes

### Module 1 Bug Fixes

#### Chat API RLS Session Fix
- **Problem**: list/delete messages endpoints returned 404 due to RLS not working
- **Fix**: `list_conversations`, `delete_conversation`, `list_messages` now call `supabase.auth.set_session()` before queries

#### Message Display Fix
- **Problem**: Clicking conversation didn't show messages
- **Fix**: `ChatPage` and `ChatWindow` now share state via props instead of each calling `useChat()` independently

#### Assistant Message Storage Fix
- **Problem**: Assistant replies weren't stored in database
- **Fix**: Now inserts new assistant message instead of trying to UPDATE user message

#### LangSmith Tracing Fix
- **Problem**: LangSmith traces not appearing in dashboard
- **Fix**: `config.py` now sets `os.environ` vars in `Settings.__init__()` before modules load

#### Startup Scripts
- Added `start.bat`, `start.sh`, `stop.bat`, `stop.sh` for convenient service management

---

### Module 2 Bug Fixes

#### Login Stuck at "Logging in..."
- **Problem**: Login page stuck at "Logging in..." after successful auth
- **Root Cause**: TypeScript compilation errors - missing `provider` parameter in `createChatStream` call, type mismatches
- **Fix**: Added `'minimax'` as provider parameter, corrected types in ChatPage and useChat

#### React Tabs Component Warning
- **Problem**: React warning about unknown `onValueChange` property being passed to non-tab children
- **Fix**: Rewrote Tabs component to only pass props to recognized children (children with valid Tab props)

#### Chat Answered Twice
- **Problem**: User asked once but AI answered twice, frontend rendered duplicate messages
- **Root Cause**: React StrictMode causing double invocation of useChat hook
- **Fix**: Added `isSendingRef` protection in useChat hook to prevent double-send

#### LangSmith Tracing Stopped Working
- **Problem**: LangSmith traces not appearing in dashboard
- **Root Cause**: `@traceable` decorator only applied to old openai_service, not new MiniMaxProvider and OllamaProvider
- **Fix**: Added `@traceable(project_name=settings.langsmith_project, run_name="chat_completion")` to both new providers

#### UI Layout Simplification
- **Problem**: Frontend UI was cluttered and unclear
- **Fix**: Rewrote Chat.tsx, ConversationList.tsx, MessageInput.tsx, DocumentUpload.tsx, DocumentList.tsx for cleaner design with tabs

#### Document Upload 403 Forbidden
- **Problem**: Document upload returned 403 Forbidden error
- **Root Cause**: Database migrations not executed - tables didn't exist
- **Fix**: Created and executed migration SQL files (003_documents_table.sql, 004_document_chunks_table.sql)

#### MiniMax Embedding API Errors
- **Problem**: Embedding generation failed with API errors
- **Root Causes & Fixes**:
  - Missing `texts` parameter (used `input`) → Changed payload to use `texts`
  - Missing `type: "db"` parameter → Added to payload (MiniMax requirement)
  - Insufficient balance → User updated API key

#### VECTOR Dimension Mismatch
- **Problem**: Embedding storage failed with dimension mismatch (1024 vs 1536)
- **Root Cause**: Migration SQL had VECTOR(1024) but MiniMax embeddings are 1536 dimensions
- **Fix**: Updated 004_document_chunks_table.sql to use VECTOR(1536), user recreated table

#### Document Status Not Updating (Frontend)
- **Problem**: After upload, frontend showed "pending" status and "0 chunks"
- **Root Cause**: `loadDocuments` only called on token change, not when switching to Documents tab
- **Fix**: Added useEffect to reload documents when tab changes to 'documents'

#### **Critical: RLS UPDATE Policy Missing**
- **Problem**: Document status remained "pending" despite chunks being created, `result.data = []` on update
- **Root Cause**:
  1. `documents` table was missing UPDATE RLS policy
  2. `document_chunks` table was also missing UPDATE RLS policy
  3. Update queries didn't include `user_id` filter, causing RLS to block updates
- **Fix**:
  - Added UPDATE policy to migration 003: `CREATE POLICY "Users can update own documents" ON public.documents FOR UPDATE USING (auth.uid() = user_id);`
  - Added UPDATE policy to migration 004: `CREATE POLICY "Users can update own chunks" ON public.document_chunks FOR UPDATE USING (auth.uid() = user_id);`
  - Updated ingestion_service.py to include `.eq("user_id", user_id)` in update queries
  - Updated documents.py upload endpoint to include user_id in SELECT query

#### RAG Stream Assistant Message Not Saved
- **Problem**: RAG-enhanced chat responses were not saved to database
- **Root Cause**: Stream loop didn't exit after sending `done` event - continued trying to yield after frontend closed connection
- **Fix**: Added `break` after `done=True` to properly exit stream loop, added try-except around yield statements

#### Token Cache User.get() AttributeError
- **Problem**: Supabase auth calls happening on every request despite caching implementation
- **Root Cause**: `gotrue.types.User` object has no `.get()` method, causing exception when logging user ID
- **Fix**: Added `_get_user_id()` helper function to safely extract user ID regardless of object type

#### Message Display: User Question Disappeared
- **Problem**: After AI responded, user's question disappeared from chat (only AI reply visible)
- **Root Cause**: Code was replacing user message with AI response instead of keeping both
- **Fix**: Modified `sendMessage` to add assistant message instead of replacing user message

---

## New Features Added (Post-Module 2 Plan)

### RAG Retrieval Implementation
- **New File**: `backend/app/services/retrieval_service.py`
  - `retrieve_relevant_chunks()` - Vector similarity search using query embedding
  - `get_context_for_query()` - Formats retrieved chunks into context string
- **New Migration**: `backend/scripts/migrations/005_match_chunks_function.sql`
  - `match_document_chunks()` - PostgreSQL function for vector similarity search with RLS
- **Chat API Integration**:
  - `build_messages()` now accepts optional `rag_context` parameter
  - Adds system message with retrieved document context when available
  - `stream_chat()` calls `RetrievalService.get_context_for_query()` before LLM call

### RAG Current Behavior
- **Current**: Every chat message triggers RAG retrieval (generates query embedding, searches vector DB)
- **Impact**: Even casual conversations consume embedding API calls
- **Optimization needed**: Add RAG toggle or keyword-based trigger to avoid unnecessary embedding calls

### Documents Tab UI Enhancement
- **Left Sidebar**: Upload component (drag & drop or click to upload)
- **Right Main Area**: Document list view with "Your Documents" header
- **Files**:
  - `frontend/src/pages/Chat.tsx` - Updated layout
  - `frontend/src/components/documents/DocumentsView.tsx` - New component for right side document display

### Logout Button
- **Location**: Top-right of sidebar header
- **Behavior**: Click shows confirmation dialog "Are you sure to logout?" before logging out
- **File**: `frontend/src/pages/Chat.tsx`

### Logging System
- **Backend**: Python logging to `log/backend.log`
  - FastAPI startup/shutdown events
  - Ingestion service logs
  - Embedding service logs
- **Frontend**: JavaScript logging to `log/frontend.log`
  - Uses `frontend/src/lib/logger.ts`
  - Sends logs to backend via `/api/logs` endpoint
  - Backend writes to `log/frontend.log`
- **Files**:
  - `backend/app/main.py` - Logging configuration
  - `backend/app/api/logs.py` - New log endpoint
  - `frontend/src/lib/logger.ts` - Frontend logger
- **gitignore**: `log/` folder is ignored

### Resizable Split Pane Layout
- **Change**: Modified from stacked tabs to side-by-side 50%-50% layout
- **Feature**: Draggable divider to resize left/right panels
- **Range**: 20% - 80% (clamped)
- **Files**: `frontend/src/pages/Chat.tsx`

### Conversation Rename
- **Feature**: Hover on conversation → pencil icon → inline rename
- **Backend**: `PATCH /api/chat/conversations/{id}` endpoint
- **Frontend**: Inline editing with Enter/Escape support
- **Files**:
  - `backend/app/api/chat.py` - New PATCH endpoint
  - `backend/app/schemas/chat.py` - Added `ConversationUpdate` schema
  - `frontend/src/lib/api.ts` - Added `updateConversation` API method
  - `frontend/src/hooks/useChat.ts` - Added `renameConversation` method
  - `frontend/src/components/chat/ConversationList.tsx` - Inline edit UI

### Token Caching (Auth Optimization)
- **Purpose**: Reduce Supabase `/auth/v1/user` calls
- **Implementation**: 5-minute in-memory cache in `backend/app/deps.py`
- **Cache**: `{token: (user_object, expiry_timestamp)}`
- **Functions**: `_get_cached_user()`, `_set_cached_user()`, `_invalidate_cached_user()`
- **Benefit**: Multiple API calls within 5 minutes only call Supabase once

### kikiKen Branding
- **Change**: Renamed application title from "Agentic RAG" to "kikiKen"
- **File**: `frontend/src/pages/Chat.tsx`

---

## Environment Configuration

### `backend/.env`:
```bash
# Supabase
SUPABASE_URL=https://oxbxlcpsdkjnoswsilli.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

# MiniMax (chat + embeddings)
MINIMAX_API_KEY=<your-minimax-api-key>
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Default LLM Provider
DEFAULT_LLM_PROVIDER=minimax

# LangSmith
LANGSMITH_API_KEY=<your-langsmith-key>
LANGSMITH_TRACING=true
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

## Database Migrations

Migrations are located in `backend/scripts/migrations/`:
- `002_enable_pgvector.sql` - Enable pgvector extension
- `003_documents_table.sql` - Documents table with RLS (SELECT, INSERT, UPDATE, DELETE)
- `004_document_chunks_table.sql` - Document chunks table with RLS and vector index
- `005_match_chunks_function.sql` - Vector similarity search function (match_document_chunks)

**Important**: All tables have full RLS coverage (SELECT, INSERT, UPDATE, DELETE policies).

## Test Documents
- Located in `test_docs/` directory
- Added to `.gitignore`
- Files: `python_guide.txt`, `machine_learning_intro.txt`, `rag_explained.txt`, `agentic_rag_project.txt`, `宝马汽车使用手册.txt`, `梁健梁晋.txt`
- HTML flowcharts: `产品使用流程图.html`, `产品使用流程详解.html`
