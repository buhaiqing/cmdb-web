# FRONTEND KNOWLEDGE BASE

**Generated:** 2025-03-29

## OVERVIEW

Vue 3 + TypeScript + Pinia + Element Plus SPA for CMDB management. Uses Composition API with `<script setup>` throughout.

## STRUCTURE

```
frontend/
├── src/
│   ├── api/           # Axios wrappers + typed API modules
│   ├── components/    # Reusable UI components (DataTable, etc.)
│   ├── router/        # Vue Router with auth guards
│   ├── stores/        # Pinia stores (user, ci)
│   ├── types/         # TypeScript interfaces
│   ├── utils/         # Helpers (validators, formatters, constants)
│   └── views/         # Page components (ci/, dashboard/, login.vue)
├── mock/              # MSW handlers + shared mock data
└── tests/e2e/         # Playwright E2E tests (see separate AGENTS.md)
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Login/auth flow | `src/views/Login.vue`, `src/stores/user.ts`, `src/api/auth.ts` |
| CI management | `src/views/ci/`, `src/api/ci.ts`, `src/stores/ci.ts` |
| API client config | `src/api/request.ts` (baseURL, interceptors, error handling) |
| Route guards | `src/router/index.ts` (check `!!userStore.token`) |
| Reusable table | `src/components/DataTable.vue` (typed props/emits, slots) |
| Form validation | `src/utils/validators.ts` |
| Mock data | `mock/data.ts`, `mock/handlers.ts` |

## CONVENTIONS

- **Components**: Always `<script setup lang="ts">` with defineProps/defineEmits
- **API Calls**: Use `http.get<T>()`, `http.post<T>()` from `src/api/request.ts`
- **State**: Pinia stores with `defineStore('name', () => {...})` pattern
- **Types**: Shared types in `src/types/index.ts`; API response types in `src/api/*.ts`
- **Selectors**: Use `data-testid` attributes for E2E tests

## ANTI-PATTERNS

- **NEVER** use Options API (`export default { data() {...} }`)
- **NEVER** skip `!!userStore.token` in router guard (Ref objects always truthy)
- **NEVER** use `localStorage` directly for token - use store actions
- **NEVER** duplicate `ApiResponse` type - use single definition

## COMMANDS

```bash
npm run dev           # Start dev server
npm run test:e2e      # Run Playwright tests
npm run test:e2e:ui   # Run tests with UI mode
npm run build         # Production build
```

## NOTES

- `baseURL: '/api'` in Axios client; Vite proxies to backend or MSW mocks
- Token persisted in localStorage but synced with Pinia store
- All forms use Element Plus `ElForm` with `ref<FormInstance>()` typing