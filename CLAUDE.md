# CLAUDE.md

RAG app with chat (default) and document ingestion interfaces. Config via env vars, no admin UI.

## Stack
- Frontend: React + Vite + Tailwind + shadcn/ui
- Backend: Python + FastAPI
- Database: Supabase (Postgres, pgvector, Auth, Storage, Realtime)
- LLM: OpenAI (Module 1), OpenRouter (Module 2+)
- Observability: LangSmith

## Rules
- Python backend must use a `venv` virtual environment
- No LangChain, no LangGraph - raw SDK calls only
- Use Pydantic for structured LLM outputs
- All tables need Row-Level Security - users only see their own data
- Stream chat responses via SSE
- Use Supabase Realtime for ingestion status updates
- Module 2+ uses stateless completions - store and send chat history yourself
- Ingestion is manual file upload only - no connectors or automated pipelines

## Planning
- Save all plans to `.agent/plans/` folder
- Naming convention: `{sequence}.{plan-name}.md` (e.g., `1.auth-setup.md`, `2.document-ingestion.md`)
- Plans should be detailed enough to execute without ambiguity
- Each task in the plan must include at least one validation test to verify it works
- Assess complexity and single-pass feasibility - can an agent realistically complete this in one go?
- Include a complexity indicator at the top of each plan:
  - ✅ **Simple** - Single-pass executable, low risk
  - ⚠️ **Medium** - May need iteration, some complexity
  - 🔴 **Complex** - Break into sub-plans before executing

## Development Flow
1. **Plan** - Create a detailed plan and save it to `.agent/plans/`
2. **Build** - Execute the plan to implement the feature
3. **Validate** - Test and verify the implementation works correctly. Use browser testing where applicable via an appropriate MCP
4. **Iterate** - Fix any issues found during validation

## Progress
Check PROGRESS.md for current module status. Update it as you complete tasks.

## Testing

**IMPORTANT**: When building new features, you MUST update the test suite to cover the new functionality.

### Test Suite Structure

| Layer | Framework | Location |
|-------|-----------|----------|
| Backend | pytest | `backend/tests/` |
| Frontend | Vitest + Testing Library | `frontend/src/test/` |

### Test Requirements

1. **All new features MUST have tests** before marking a module as complete
2. **Backend tests** go in `backend/tests/test_*.py`
3. **Frontend tests** go in `frontend/src/test/**/*.test.tsx`
4. **Each API endpoint** must have tests for success and error cases
5. **Each component** should have tests for render and user interactions

### Test Coverage Targets

- Backend: ≥80% code coverage
- Frontend: ≥70% component coverage
- Critical paths (auth, chat): 100% coverage

### Running Tests

```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm test

# With coverage
cd backend && pytest tests/ --cov=app --cov-report=html
```

### CI/CD

Tests run automatically on push via `.github/workflows/test.yml`. All tests must pass before merging.