# BACKEND KNOWLEDGE BASE

**Generated:** 2025-03-29

## OVERVIEW

FastAPI REST API for CMDB with SQLAlchemy ORM, Pydantic schemas, and JWT authentication. Service-layer architecture separates business logic from routes.

## STRUCTURE

```
backend/
├── app/
│   ├── api/           # Route modules (auth, ci, user, health)
│   │   └── routes/    # FastAPI routers with path operations
│   ├── core/          # Config, exceptions, security (JWT)
│   ├── db/            # SQLAlchemy session, engine, init
│   ├── middleware/    # Auth + logging middleware
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic request/response schemas
│   └── services/      # Business logic layer
└── tests/             # pytest unit/integration tests
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Auth endpoints | `app/api/routes/auth.py`, `app/services/auth_service.py` |
| CI CRUD | `app/api/routes/ci.py`, `app/services/ci_service.py` |
| User management | `app/api/routes/user.py`, `app/services/user_service.py` |
| DB models | `app/models/ci.py` (polymorphic CI types), `app/models/user.py` |
| Response schemas | `app/schemas/common.py` (BaseResponse, PaginatedResponse) |
| JWT logic | `app/core/security.py`, `app/services/auth_service.py` |
| Config | `app/core/config.py` (env vars, defaults) |
| Middleware | `app/middleware/auth.py` (token validation) |

## CONVENTIONS

- **Routes**: Use `APIRouter()` with `response_model=Schema`, prefix in `__init__.py`
- **Schemas**: Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
- **Services**: Inject `db: Session` via constructor; raise custom exceptions
- **Models**: Inherit from `Base` with `TimestampMixin`; use Enums for status
- **Exceptions**: Use `app/core/exceptions.py` types (NotFound, Unauthorized, etc.)

## ANTI-PATTERNS

- **NEVER** put business logic in route handlers - use services
- **NEVER** use `Base.metadata.create_all()` in production - use Alembic
- **NEVER** hardcode page_size in routes - use config constants
- **NEVER** store JSON strings for tags - consider proper JSON field or normalized table

## COMMANDS

```bash
uvicorn app.main:app --reload   # Start dev server
pytest --cov=app                # Run tests with coverage
pytest -m unit                  # Run only unit tests
pytest -m integration           # Run integration tests
alembic revision --autogenerate -m "message"  # Create migration
alembic upgrade head            # Apply migrations
```

## NOTES

- Default DB is SQLite (`./cmdb.db`); production should use PostgreSQL
- JWT tokens via `jose` library; secret from `settings.secret_key`
- Middleware handles auth for all routes except login/register/health/docs
- CI model is polymorphic: base `ConfigurationItem` + per-type tables