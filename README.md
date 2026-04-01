# Cloud Code Agentic RAG

Build an agentic RAG application from scratch by collaborating with Claude Code. Follow along with our video series using the docs in this repo.

## What This Is

A hands-on course where you collaborate with Claude Code to build a full-featured RAG system. You're not the one writing code—Claude is. Your job is to guide it, understand what you're building, and course-correct when needed.

**You don't need to know how to code.** You do need to be technically minded and willing to learn about APIs, databases, and system architecture.

## What You'll Build

- **Chat interface** with threaded conversations, streaming, tool calls, and subagent reasoning
- **Document ingestion** with drag-and-drop upload and processing status
- **Full RAG pipeline**: chunking, embedding, hybrid search, reranking
- **Agentic patterns**: text-to-SQL, web search, subagents with isolated context

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React, TypeScript, Tailwind, shadcn/ui, Vite |
| Backend | Python, FastAPI |
| Database | Supabase (Postgres + pgvector + Auth + Storage) |
| Doc Processing | Docling |
| AI Models | Local (LM Studio) or Cloud (OpenAI, OpenRouter, MiniMax) |
| Observability | LangSmith |

## The 8 Modules

| # | Module | Status |
|---|--------|--------|
| 1 | **App Shell + Observability** — Auth, chat UI, managed RAG with OpenAI Responses API | Completed |
| 2 | **BYO Retrieval + Memory** — Ingestion, pgvector, switch to generic completions API | Completed |
| 3 | **Record Manager** — Content hashing, deduplication | Completed |
| 4 | **Metadata Extraction** — LLM-extracted metadata, filtered retrieval | Completed |
| 5 | **Multi-Format Support** — PDF, DOCX, HTML, Markdown via Docling | Completed |
| 6 | **Hybrid Search & Reranking** — Keyword + vector search, RRF, reranking | Completed |
| 7 | **Additional Tools** — Text-to-SQL, web search fallback | Completed |
| 8 | **Subagents** — Isolated context, document analysis delegation | In Progress |

## Getting Started

1. Clone this repo
2. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
3. Open in your IDE (Cursor, VS Code, etc.)
4. Run `claude` in the terminal
5. Use the `/onboard` command to get started

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints (auth, chat, documents, logs)
│   │   ├── services/      # Business logic (ingestion, retrieval, embedding, etc.)
│   │   ├── schemas/       # Pydantic models
│   │   └── supabase.py    # Database client
│   ├── tests/             # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components (chat, documents, ui)
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   └── test/          # Vitest test suite
│   └── package.json
├── scripts/
│   └── supabase/migrations/  # Database migrations
├── .agent/plans/          # Build plans for each module
└── CLAUDE.md              # Claude Code context
```

## Docs

- [PRD.md](./PRD.md) — What to build (the 8 modules in detail)
- [CLAUDE.md](./CLAUDE.md) — Context for Claude Code
- [PROGRESS.md](./PROGRESS.md) — Track your build progress

## Test Accounts

| Service | Credentials |
|---------|-------------|
| Supabase | https://oxbxlcpsdkjnoswsilli.supabase.co |
| Email | test@test.com |
| Password | kC8u+jyJ*hF66si |

## Quick Commands

```bash
# Start both services
./scripts/project/start.sh

# Stop all services
./scripts/project/stop.sh

# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm test
```
