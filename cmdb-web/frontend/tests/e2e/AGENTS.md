# E2E TESTS KNOWLEDGE BASE

**Generated:** 2025-03-29

## OVERVIEW

Playwright-based E2E tests using Page Object Model and MSW/API mocking. Tests cover auth, CI management, changes, and audit flows.

## STRUCTURE

```
tests/e2e/
├── fixtures/         # Playwright fixtures + test data factories
│   ├── index.ts      # Extended test fixture with page objects
│   └── factories.ts  # UserFactory, CIFactory for test data
├── pages/            # Page Object Model
│   ├── index.ts      # LoginPage, CIListPage, etc.
│   ├── base.page.ts  # BasePage with common helpers
│   └── selectors.ts  # Centralized data-testid selectors
├── utils/            # Test utilities
│   ├── api-mock.ts   # Playwright route interception setup
│   └── test-helpers.ts
├── *.test.ts         # Test files by domain (auth, ci, change, etc.)
├── playwright.config.ts
└── global-setup.ts
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Add new test | Create `feature.test.ts` in root |
| Add page object | `pages/index.ts` + extend `BasePage` |
| Add test data | `fixtures/factories.ts` |
| Mock API | `utils/api-mock.ts` (imports from `mock/data.ts`) |
| Configure tests | `playwright.config.ts` |
| Find selectors | `pages/selectors.ts` |

## CONVENTIONS

- **Test IDs**: Name tests like `AUTH-001: test description`
- **Page Objects**: Extend `BasePage`, use fluent methods
- **Fixtures**: Import `test, expect` from `./fixtures/index`
- **API Mocks**: Call `setupApiMocks(page)` before navigation
- **Selectors**: Use `data-testid` attributes; define in `selectors.ts`

## ANTI-PATTERNS

- **NEVER** use CSS selectors that may change - use `data-testid`
- **NEVER** duplicate mock data - import from `mock/data.ts`
- **NEVER** commit `playwright-report/` or test artifacts
- **NEVER** forget to set `baseURL` in config

## COMMANDS

```bash
npx playwright test                  # Run all tests
npx playwright test --ui             # UI mode
npx playwright test -g "AUTH"        # Run specific tests
npx playwright test --browser=webkit # Specific browser
npx playwright show-report           # View HTML report
```

## NOTES

- Tests use MSW mock data from `frontend/mock/data.ts`
- `setupApiMocks()` uses Playwright `page.route()` for interception
- CI mode: `retries: 2`, `workers: 1` for stability
- Global setup in `global-setup.ts` runs once before all tests