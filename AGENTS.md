# CMDB-WEB PROJECT KNOWLEDGE BASE

**Generated:** 2025-03-29
**Commit:** current
**Branch:** main

## OVERVIEW

CMDB (Configuration Management Database) web application with Vue 3 frontend and FastAPI backend. Manages configuration items, change requests, and audit logs for IT infrastructure.

**Stack**: Vue 3 + TypeScript + Pinia + Element Plus (frontend) | Python + FastAPI + SQLAlchemy (backend)

## STRUCTURE

```
cmdb-web/
├── cmdb-web/
│   ├── frontend/       # Vue 3 + TypeScript SPA
│   │   ├── src/        # Source code (views, components, stores, api)
│   │   ├── mock/       # MSW mock data for development
│   │   └── tests/e2e/  # Playwright E2E tests
│   └── backend/        # FastAPI REST API
│       └── app/        # Routes, services, models, schemas
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new page/view | `frontend/src/views/` | Use script setup + Composition API |
| Add new API endpoint | `frontend/src/api/` + `backend/app/api/routes/` | Follow existing patterns |
| Modify CI management | `frontend/src/views/ci/` + `backend/app/api/routes/ci.py` | Core domain logic |
| Add Pinia store | `frontend/src/stores/` | Use defineStore with composition API |
| Add E2E test | `frontend/tests/e2e/` | Use Page Object Model |
| Add backend test | `backend/tests/` | Use pytest with in-memory SQLite |
| Mock API for dev | `frontend/mock/handlers.ts` | MSW handlers |

## CONVENTIONS

### Frontend
- **Components**: Use `<script setup lang="ts">` for all Vue components
- **Props/Emits**: Use `defineProps<T>()` and `defineEmits<T>()` with TypeScript
- **API**: All responses wrapped in `ApiResponse<T>` (success, data, error)
- **State**: Pinia stores with composition API pattern
- **Routes**: Router with guards checking `!!userStore.token`

### Backend
- **Routes**: FastAPI routers under `/api` prefix
- **Schemas**: Pydantic models with `model_config = ConfigDict(from_attributes=True)`
- **Services**: Business logic in `app/services/`, not in routes
- **Models**: SQLAlchemy with `Base` class and `TimestampMixin`
- **Responses**: Use `BaseResponse` and `PaginatedResponse` schemas

## ANTI-PATTERNS (THIS PROJECT)

- **NEVER** use `as any` or `@ts-ignore` in frontend
- **NEVER** store tokens in localStorage in production (use HttpOnly cookies)
- **NEVER** skip `response.data` unwrap in Axios interceptor
- **NEVER** forget `!!` for boolean check on Vue Ref objects
- **NEVER** use `Base.metadata.create_all()` in production startup (use Alembic migrations)
- **NEVER** commit `dist/`, `playwright-report/`, `.DS_Store`, or `.omc/`

## COMMANDS

```bash
# Frontend development
cd cmdb-web/frontend
npm run dev          # Start dev server (http://localhost:3000)
npm run test:e2e     # Run Playwright E2E tests
npm run build        # Build for production

# Backend development
cd cmdb-web/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start dev server
pytest --cov=app --cov-report=html  # Run tests with coverage
```

## NOTES

- **Auth**: JWT tokens via `/api/auth/login`, stored in localStorage + Pinia store
- **Mock Data**: Development uses MSW for API mocking; tests use Playwright route interception
- **Testing**: Frontend E2E tests use Page Object Model; backend uses pytest with isolated SQLite
- **CI**: Test artifacts should be gitignored; use `.gitignore` rules for generated files