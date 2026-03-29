# Rust 后端开发规范

> **版本**: Rust 1.75+  
> **框架**: Axum / Actix-web  
> **标准**: 企业级生产规范

---

## 1. 技术栈

| 类别 | 技术选型 | 版本 |
|------|----------|------|
| 语言 | Rust | 1.75+ |
| Web框架 | Axum / Actix-web | latest |
| ORM | Sea-ORM / Diesel | latest |
| 数据库驱动 | sqlx / tokio-postgres | latest |
| 测试 | tokio-test / mockall | latest |
| 日志 | tracing / log | latest |
| 配置 | config-rs | latest |
| 验证 | validator | latest |
| 文档 | utoipa (OpenAPI) | latest |
| 监控 | metrics / prometheus | latest |
| 追踪 | opentelemetry-rust | latest |
| 异步运行时 | Tokio | 1.x |
| 序列化 | serde | latest |
| HTTP客户端 | reqwest | latest |

---

## 2. 项目结构

```
project/
├── Cargo.toml
├── Cargo.lock
├── .env
├── .env.example
├── rustfmt.toml
├── clippy.toml
├── src/
│   ├── main.rs                 # 应用入口
│   ├── lib.rs                  # 库入口
│   ├── config/                 # 配置模块
│   │   ├── mod.rs
│   │   └── settings.rs
│   ├── domain/                 # 领域模型
│   │   ├── mod.rs
│   │   ├── user.rs
│   │   └── order.rs
│   ├── application/            # 应用层
│   │   ├── mod.rs
│   │   ├── commands/           # 命令处理
│   │   └── queries/            # 查询处理
│   ├── infrastructure/         # 基础设施层
│   │   ├── mod.rs
│   │   ├── persistence/        # 数据持久化
│   │   │   ├── mod.rs
│   │   │   ├── models.rs
│   │   │   └── repositories.rs
│   │   ├── web/                # Web层
│   │   │   ├── mod.rs
│   │   │   ├── handlers.rs
│   │   │   ├── middleware.rs
│   │   │   └── routes.rs
│   │   └── logging.rs
│   └── shared/                 # 共享组件
│       ├── mod.rs
│       ├── error.rs
│       └── validation.rs
├── tests/                      # 集成测试
│   ├── integration_tests.rs
│   └── helpers/
├── migrations/                 # 数据库迁移
│   └── ...
├── docs/                       # 文档
├── scripts/                    # 脚本
└── docker/
    └── Dockerfile
```

---

## 3. 代码规范

### 3.1 命名规范

```rust
// 包/模块名: snake_case
mod user_service;
mod order_repository;

// 结构体/枚举/特质名: PascalCase
struct User {
    id: Uuid,
    email: String,
}

enum OrderStatus {
    Pending,
    Confirmed,
    Shipped,
    Delivered,
}

trait Repository<T> {
    async fn find_by_id(&self, id: Uuid) -> Result<Option<T>, Error>;
    async fn save(&self, entity: &T) -> Result<(), Error>;
}

// 变量/函数名: snake_case
let user_name = "john";
let user_id = Uuid::new_v4();

async fn create_user(
    pool: &PgPool,
    request: CreateUserRequest,
) -> Result<User, Error> {
    // ...
}

// 常量: SCREAMING_SNAKE_CASE
const MAX_RETRY_COUNT: u32 = 3;
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);

// 类型别名: PascalCase
type UserId = Uuid;
type Result<T> = std::result::Result<T, Error>;

// 生命周期参数: 'a, 'b
fn process_data<'a, 'b>(
    input: &'a str,
    config: &'b Config,
) -> &'a str {
    input
}

// 泛型参数: T, E, K, V
struct Container<T> {
    data: T,
}

fn transform<T, E>(input: T) -> Result<T, E> {
    Ok(input)
}
```

### 3.2 错误处理

```rust
// src/shared/error.rs
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Resource not found")]
    NotFound,
    
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    
    #[error("Unauthorized")]
    Unauthorized,
    
    #[error("Forbidden")]
    Forbidden,
    
    #[error("Database error")]
    Database(#[from] sqlx::Error),
    
    #[error("Validation error")]
    Validation(#[from] validator::ValidationErrors),
    
    #[error("Internal server error")]
    Internal,
    
    #[error("External service error: {0}")]
    ExternalService(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_message) = match &self {
            AppError::NotFound => (StatusCode::NOT_FOUND, self.to_string()),
            AppError::InvalidInput(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            AppError::Unauthorized => (StatusCode::UNAUTHORIZED, self.to_string()),
            AppError::Forbidden => (StatusCode::FORBIDDEN, self.to_string()),
            AppError::Database(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Database error".to_string()),
            AppError::Validation(_) => (StatusCode::BAD_REQUEST, "Validation failed".to_string()),
            AppError::Internal => (StatusCode::INTERNAL_SERVER_ERROR, self.to_string()),
            AppError::ExternalService(msg) => (StatusCode::BAD_GATEWAY, msg.clone()),
        };
        
        let body = Json(json!({
            "error": error_message,
            "code": status.as_u16(),
        }));
        
        (status, body).into_response()
    }
}

pub type Result<T> = std::result::Result<T, AppError>;

// 使用示例
use crate::shared::error::{AppError, Result};

pub async fn get_user(pool: &PgPool, id: Uuid) -> Result<User> {
    let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = $1")
        .bind(id)
        .fetch_optional(pool)
        .await
        .map_err(AppError::Database)?;
    
    user.ok_or(AppError::NotFound)
}
```

### 3.3 异步编程

```rust
use tokio::time::{sleep, Duration, timeout};
use futures::future::join_all;

// 基本异步函数
pub async fn fetch_user_data(user_id: Uuid) -> Result<UserData> {
    // 模拟异步操作
    sleep(Duration::from_millis(100)).await;
    
    Ok(UserData {
        id: user_id,
        name: "John".to_string(),
    })
}

// 超时处理
pub async fn fetch_with_timeout() -> Result<UserData> {
    let result = timeout(
        Duration::from_secs(5),
        fetch_user_data(Uuid::new_v4())
    ).await;
    
    match result {
        Ok(Ok(data)) => Ok(data),
        Ok(Err(e)) => Err(e),
        Err(_) => Err(AppError::ExternalService("Timeout".to_string())),
    }
}

// 并发处理
pub async fn fetch_multiple_users(user_ids: Vec<Uuid>) -> Vec<Result<UserData>> {
    let futures: Vec<_> = user_ids
        .into_iter()
        .map(|id| fetch_user_data(id))
        .collect();
    
    join_all(futures).await
}

// 使用 spawn 创建任务
pub async fn process_users_concurrently(users: Vec<User>) {
    let mut handles = vec![];
    
    for user in users {
        let handle = tokio::spawn(async move {
            process_user(user).await
        });
        handles.push(handle);
    }
    
    for handle in handles {
        if let Err(e) = handle.await {
            eprintln!("Task failed: {:?}", e);
        }
    }
}

// 使用 channel 进行通信
use tokio::sync::mpsc;

pub async fn worker_pool() {
    let (tx, mut rx) = mpsc::channel::<WorkItem>(100);
    
    // 启动多个 worker
    for id in 0..4 {
        let worker_rx = rx.resubscribe();
        tokio::spawn(async move {
            worker(id, worker_rx).await;
        });
    }
    
    // 发送工作项
    for i in 0..100 {
        tx.send(WorkItem { id: i }).await.unwrap();
    }
}
```

---

## 4. Web 框架规范

### 4.1 Axum 框架

```rust
// src/main.rs
use axum::{
    routing::{get, post, put, delete},
    Router,
    extract::{State, Path, Query},
    Json,
};
use std::net::SocketAddr;
use tower::ServiceBuilder;
use tower_http::{
    cors::CorsLayer,
    trace::TraceLayer,
    compression::CompressionLayer,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 初始化日志
    tracing_subscriber::fmt::init();
    
    // 加载配置
    let config = Config::from_env()?;
    
    // 创建数据库连接池
    let pool = create_pool(&config.database).await?;
    
    // 运行迁移
    sqlx::migrate!("./migrations").run(&pool).await?;
    
    // 创建应用状态
    let state = AppState {
        pool,
        config: config.clone(),
    };
    
    // 构建路由
    let app = create_router(state);
    
    // 启动服务器
    let addr = SocketAddr::from(([0, 0, 0, 0], config.server.port));
    tracing::info!("Server starting on {}", addr);
    
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    
    Ok(())
}

fn create_router(state: AppState) -> Router {
    Router::new()
        // 健康检查
        .route("/health", get(health_check))
        // API v1
        .nest("/api/v1", api_routes())
        // 全局中间件
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive())
                .layer(CompressionLayer::new())
                .layer(axum::middleware::from_fn(auth_middleware)),
        )
        .with_state(state)
}

fn api_routes() -> Router<AppState> {
    Router::new()
        .nest("/users", user_routes())
        .nest("/orders", order_routes())
}

fn user_routes() -> Router<AppState> {
    Router::new()
        .route("/", get(list_users).post(create_user))
        .route("/:id", get(get_user).put(update_user).delete(delete_user))
}

// Handler 示例
use serde::{Deserialize, Serialize};
use validator::Validate;
use uuid::Uuid;

#[derive(Debug, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(email)]
    pub email: String,
    
    #[validate(length(min = 2, max = 50))]
    pub name: String,
    
    #[validate(length(min = 8))]
    pub password: String,
}

#[derive(Debug, Serialize)]
pub struct UserResponse {
    pub id: Uuid,
    pub email: String,
    pub name: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

pub async fn create_user(
    State(state): State<AppState>,
    Json(request): Json<CreateUserRequest>,
) -> Result<Json<UserResponse>, AppError> {
    // 验证请求
    request.validate()?;
    
    // 创建用户
    let user = sqlx::query_as::<_, User>(
        "INSERT INTO users (id, email, name, password_hash, created_at) 
         VALUES ($1, $2, $3, $4, $5) 
         RETURNING *"
    )
    .bind(Uuid::new_v4())
    .bind(&request.email)
    .bind(&request.name)
    .bind(hash_password(&request.password))
    .bind(chrono::Utc::now())
    .fetch_one(&state.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::Database(db_err) if db_err.constraint().is_some() => {
            AppError::InvalidInput("Email already exists".to_string())
        }
        _ => AppError::Database(e),
    })?;
    
    Ok(Json(UserResponse {
        id: user.id,
        email: user.email,
        name: user.name,
        created_at: user.created_at,
    }))
}

pub async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<UserResponse>, AppError> {
    let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = $1")
        .bind(id)
        .fetch_optional(&state.pool)
        .await
        .map_err(AppError::Database)?
        .ok_or(AppError::NotFound)?;
    
    Ok(Json(UserResponse {
        id: user.id,
        email: user.email,
        name: user.name,
        created_at: user.created_at,
    }))
}

pub async fn list_users(
    State(state): State<AppState>,
    Query(params): Query<ListUsersQuery>,
) -> Result<Json<PaginatedResponse<UserResponse>>, AppError> {
    let page = params.page.unwrap_or(1);
    let size = params.size.unwrap_or(10);
    let offset = (page - 1) * size;
    
    let users = sqlx::query_as::<_, User>(
        "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2"
    )
    .bind(size as i64)
    .bind(offset as i64)
    .fetch_all(&state.pool)
    .await
    .map_err(AppError::Database)?;
    
    let total: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM users")
        .fetch_one(&state.pool)
        .await
        .map_err(AppError::Database)?;
    
    let responses: Vec<UserResponse> = users
        .into_iter()
        .map(|u| UserResponse {
            id: u.id,
            email: u.email,
            name: u.name,
            created_at: u.created_at,
        })
        .collect();
    
    Ok(Json(PaginatedResponse {
        data: responses,
        total,
        page,
        size,
    }))
}

#[derive(Debug, Deserialize)]
pub struct ListUsersQuery {
    pub page: Option<i64>,
    pub size: Option<i64>,
}

#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T> {
    pub data: Vec<T>,
    pub total: i64,
    pub page: i64,
    pub size: i64,
}

pub async fn health_check() -> &'static str {
    "OK"
}
```

### 4.2 中间件

```rust
// src/infrastructure/web/middleware.rs
use axum::{
    extract::{Request, State},
    middleware::Next,
    response::Response,
};
use tracing::{info, warn};

pub async fn auth_middleware(
    State(state): State<AppState>,
    mut request: Request,
    next: Next,
) -> Result<Response, AppError> {
    // 提取 token
    let token = request
        .headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .and_then(|h| h.strip_prefix("Bearer "));
    
    match token {
        Some(token) => {
            // 验证 token
            let claims = validate_token(token, &state.config.jwt_secret)
                .map_err(|_| AppError::Unauthorized)?;
            
            // 将用户信息添加到请求扩展
            request.extensions_mut().insert(claims);
            
            Ok(next.run(request).await)
        }
        None => Err(AppError::Unauthorized),
    }
}

pub async fn logging_middleware(
    request: Request,
    next: Next,
) -> Response {
    let start = std::time::Instant::now();
    let method = request.method().clone();
    let uri = request.uri().clone();
    
    info!("Request: {} {}", method, uri);
    
    let response = next.run(request).await;
    
    let duration = start.elapsed();
    let status = response.status();
    
    info!(
        "Response: {} {} - {} in {:?}",
        method, uri, status, duration
    );
    
    response
}
```

---

## 5. 数据库规范

### 5.1 SQLx 使用

```rust
// src/infrastructure/persistence/models.rs
use sqlx::FromRow;
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, FromRow)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    pub name: String,
    pub password_hash: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, FromRow)]
pub struct Order {
    pub id: Uuid,
    pub user_id: Uuid,
    pub total_amount: f64,
    pub status: OrderStatus,
    pub created_at: DateTime<Utc>,
}

// src/infrastructure/persistence/repositories.rs
use async_trait::async_trait;

#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, sqlx::Error>;
    async fn find_by_email(&self, email: &str) -> Result<Option<User>, sqlx::Error>;
    async fn save(&self, user: &User) -> Result<(), sqlx::Error>;
    async fn delete(&self, id: Uuid) -> Result<(), sqlx::Error>;
    async fn list(&self, offset: i64, limit: i64) -> Result<Vec<User>, sqlx::Error>;
    async fn count(&self) -> Result<i64, sqlx::Error>;
}

pub struct PgUserRepository {
    pool: PgPool,
}

impl PgUserRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl UserRepository for PgUserRepository {
    async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, sqlx::Error> {
        sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = $1")
            .bind(id)
            .fetch_optional(&self.pool)
            .await
    }
    
    async fn find_by_email(&self, email: &str) -> Result<Option<User>, sqlx::Error> {
        sqlx::query_as::<_, User>("SELECT * FROM users WHERE email = $1")
            .bind(email)
            .fetch_optional(&self.pool)
            .await
    }
    
    async fn save(&self, user: &User) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6)
             ON CONFLICT (id) DO UPDATE SET
             email = EXCLUDED.email,
             name = EXCLUDED.name,
             password_hash = EXCLUDED.password_hash,
             updated_at = EXCLUDED.updated_at"
        )
        .bind(user.id)
        .bind(&user.email)
        .bind(&user.name)
        .bind(&user.password_hash)
        .bind(user.created_at)
        .bind(user.updated_at)
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    async fn delete(&self, id: Uuid) -> Result<(), sqlx::Error> {
        sqlx::query("DELETE FROM users WHERE id = $1")
            .bind(id)
            .execute(&self.pool)
            .await?;
        
        Ok(())
    }
    
    async fn list(&self, offset: i64, limit: i64) -> Result<Vec<User>, sqlx::Error> {
        sqlx::query_as::<_, User>(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2"
        )
        .bind(limit)
        .bind(offset)
        .fetch_all(&self.pool)
        .await
    }
    
    async fn count(&self) -> Result<i64, sqlx::Error> {
        sqlx::query_scalar("SELECT COUNT(*) FROM users")
            .fetch_one(&self.pool)
            .await
    }
}
```

### 5.2 数据库连接池

```rust
// src/config/database.rs
use sqlx::postgres::{PgPool, PgPoolOptions};

pub async fn create_pool(config: &DatabaseConfig) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(config.max_connections)
        .min_connections(config.min_connections)
        .acquire_timeout(std::time::Duration::from_secs(config.acquire_timeout_secs))
        .idle_timeout(std::time::Duration::from_secs(config.idle_timeout_secs))
        .max_lifetime(std::time::Duration::from_secs(config.max_lifetime_secs))
        .connect(&config.url)
        .await
}
```

---

## 6. 测试规范

### 6.1 单元测试

```rust
// src/domain/user.rs
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_user_creation() {
        let user = User::new(
            "test@example.com",
            "Test User",
        );
        
        assert_eq!(user.email, "test@example.com");
        assert_eq!(user.name, "Test User");
        assert!(!user.id.is_nil());
    }
    
    #[test]
    fn test_email_validation() {
        let result = User::validate_email("invalid-email");
        assert!(result.is_err());
        
        let result = User::validate_email("valid@example.com");
        assert!(result.is_ok());
    }
}

// 异步测试
#[cfg(test)]
mod async_tests {
    use super::*;
    
    #[tokio::test]
    async fn test_user_repository() {
        // 使用内存数据库或测试容器
        let pool = create_test_pool().await;
        let repo = PgUserRepository::new(pool);
        
        let user = User::new("test@example.com", "Test");
        repo.save(&user).await.unwrap();
        
        let found = repo.find_by_id(user.id).await.unwrap();
        assert!(found.is_some());
        assert_eq!(found.unwrap().email, "test@example.com");
    }
}
```

### 6.2 集成测试

```rust
// tests/integration/users.rs
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use tower::ServiceExt;

#[tokio::test]
async fn test_create_user() {
    let app = create_test_app().await;
    
    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/v1/users")
                .header("Content-Type", "application/json")
                .body(Body::from(
                    r#"{"email":"test@example.com","name":"Test","password":"password123"}"#
                ))
                .unwrap(),
        )
        .await
        .unwrap();
    
    assert_eq!(response.status(), StatusCode::CREATED);
    
    let body = axum::body::to_bytes(response.into_body(), usize::MAX)
        .await
        .unwrap();
    let user: UserResponse = serde_json::from_slice(&body).unwrap();
    
    assert_eq!(user.email, "test@example.com");
    assert_eq!(user.name, "Test");
}
```

---

## 7. 可观测性

### 7.1 日志 (Tracing)

```rust
// src/infrastructure/logging.rs
use tracing_subscriber::{
    layer::SubscriberExt,
    util::SubscriberInitExt,
    EnvFilter,
};

pub fn init_logging() {
    tracing_subscriber::registry()
        .with(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into()),
        )
        .with(
            tracing_subscriber::fmt::layer()
                .with_target(true)
                .with_thread_ids(true)
                .with_line_number(true),
        )
        .init();
}

// 使用示例
use tracing::{info, warn, error, instrument};

#[instrument(skip(self))]
pub async fn get_user(&self, id: Uuid) -> Result<User> {
    info!(user_id = %id, "Fetching user");
    
    match self.repository.find_by_id(id).await {
        Ok(Some(user)) => {
            info!(user_id = %id, "User found");
            Ok(user)
        }
        Ok(None) => {
            warn!(user_id = %id, "User not found");
            Err(AppError::NotFound)
        }
        Err(e) => {
            error!(user_id = %id, error = %e, "Database error");
            Err(AppError::Database(e))
        }
    }
}
```

### 7.2 指标

```rust
// src/infrastructure/metrics.rs
use metrics::{counter, histogram, gauge};
use std::time::Instant;

pub fn record_http_request(method: &str, path: &str, status: u16, duration: f64) {
    counter!(
        "http_requests_total",
        "method" => method.to_string(),
        "path" => path.to_string(),
        "status" => status.to_string(),
    )
    .increment(1);
    
    histogram!(
        "http_request_duration_seconds",
        "method" => method.to_string(),
        "path" => path.to_string(),
    )
    .record(duration);
}

pub fn record_active_connections(count: usize) {
    gauge!("active_connections").set(count as f64);
}

// Axum中间件
pub async fn metrics_middleware(
    request: Request,
    next: Next,
) -> Response {
    let start = Instant::now();
    let method = request.method().clone();
    let path = request.uri().path().to_string();
    
    let response = next.run(request).await;
    
    let duration = start.elapsed().as_secs_f64();
    let status = response.status().as_u16();
    
    record_http_request(&method.to_string(), &path, status, duration);
    
    response
}
```

### 7.3 追踪

```rust
// src/infrastructure/tracing.rs
use opentelemetry::trace::TracerProvider;
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::trace::Tracer;

pub fn init_tracer(endpoint: &str) -> Tracer {
    let provider = opentelemetry_sdk::trace::TracerProvider::builder()
        .with_batch_exporter(
            opentelemetry_otlp::SpanExporter::builder()
                .with_tonic()
                .with_endpoint(endpoint)
                .build()
                .expect("Failed to create exporter"),
        )
        .with_resource(opentelemetry_sdk::Resource::new(vec![
            opentelemetry::KeyValue::new("service.name", "rust-api"),
        ]))
        .build();
    
    provider.tracer("rust-api")
}

// 使用示例
use tracing::Span;
use tracing_opentelemetry::OpenTelemetrySpanExt;

async fn process_order(order_id: Uuid) {
    let span = tracing::info_span!("process_order", order_id = %order_id);
    let _enter = span.enter();
    
    // 自动传播追踪上下文
    
    validate_order(order_id).await;
    charge_payment(order_id).await;
    send_confirmation(order_id).await;
}
```

---

## 8. 配置管理

```rust
// src/config/settings.rs
use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub jwt: JwtConfig,
    pub redis: RedisConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Deserialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct JwtConfig {
    pub secret: String,
    pub expiration_secs: i64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct RedisConfig {
    pub url: String,
}

impl Settings {
    pub fn from_env() -> Result<Self, ConfigError> {
        let config = Config::builder()
            .add_source(File::with_name("config/default").required(false))
            .add_source(File::with_name("config/local").required(false))
            .add_source(Environment::with_prefix("APP").separator("__"))
            .build()?;
        
        config.try_deserialize()
    }
}
```

---

## 9. AI Agent 集成

```rust
// src/agents/code_reviewer.rs
use reqwest::Client;
use serde::{Deserialize, Serialize};

pub struct CodeReviewer {
    client: Client,
    api_key: String,
    endpoint: String,
}

#[derive(Debug, Serialize)]
struct ReviewRequest {
    filename: String,
    content: String,
    language: String,
}

#[derive(Debug, Deserialize)]
pub struct ReviewResponse {
    pub issues: Vec<Issue>,
    pub score: u8,
}

#[derive(Debug, Deserialize)]
pub struct Issue {
    pub line: usize,
    pub severity: String,
    pub message: String,
    pub suggestion: String,
}

impl CodeReviewer {
    pub fn new(api_key: String, endpoint: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            endpoint,
        }
    }
    
    pub async fn review(&self, filename: &str, content: &str) -> Result<ReviewResponse, reqwest::Error> {
        let request = ReviewRequest {
            filename: filename.to_string(),
            content: content.to_string(),
            language: "rust".to_string(),
        };
        
        let response = self.client
            .post(&self.endpoint)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&request)
            .send()
            .await?
            .json::<ReviewResponse>()
            .await?;
        
        Ok(response)
    }
}
```

---

**参考**:
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Axum Documentation](https://docs.rs/axum/latest/axum/)
- [SQLx Documentation](https://docs.rs/sqlx/latest/sqlx/)
- [Tokio Documentation](https://tokio.rs/)
