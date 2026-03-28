# Go 后端开发规范

> **版本**: Go 1.22+  
> **框架**: Gin / Echo / Fiber  
> **标准**: 企业级生产规范

---

## 1. 技术栈

| 类别 | 技术选型 | 版本 |
|------|----------|------|
| 语言 | Go | 1.22+ |
| Web框架 | Gin / Echo / Fiber | latest |
| ORM | GORM / Ent | latest |
| 数据库驱动 | pgx / go-redis | latest |
| 测试 | testify + ginkgo | latest |
| 日志 | zap / zerolog | latest |
| 配置 | viper | latest |
| 验证 | go-playground/validator | latest |
| 文档 | swaggo/swag | latest |
| 监控 | prometheus/client_golang | latest |
| 追踪 | opentelemetry-go | v1.0+ |
| 任务调度 | asynq / machinery | latest |

---

## 2. 项目结构

```
project/
├── cmd/
│   ├── api/                    # HTTP API 入口
│   │   └── main.go
│   ├── worker/                 # 后台任务入口
│   │   └── main.go
│   └── migrate/                # 数据库迁移
│       └── main.go
├── internal/                   # 私有代码
│   ├── config/                 # 配置
│   │   └── config.go
│   ├── domain/                 # 领域模型
│   │   ├── user.go
│   │   └── order.go
│   ├── repository/             # 数据访问层
│   │   ├── user_repo.go
│   │   └── order_repo.go
│   ├── service/                # 业务逻辑层
│   │   ├── user_service.go
│   │   └── order_service.go
│   ├── handler/                # HTTP处理器
│   │   ├── user_handler.go
│   │   └── order_handler.go
│   ├── middleware/             # 中间件
│   │   ├── auth.go
│   │   ├── logging.go
│   │   └── recovery.go
│   └── pkg/                    # 内部工具包
│       ├── logger/
│       ├── validator/
│       └── errors/
├── pkg/                        # 公共库 (可被外部导入)
│   ├── utils/
│   └── constants/
├── api/                        # API定义
│   ├── swagger/                # Swagger文档
│   └── proto/                  # Protocol Buffers
├── web/                        # 静态文件
├── configs/                    # 配置文件
│   ├── config.yaml
│   └── config.prod.yaml
├── deployments/                # 部署配置
│   ├── docker/
│   └── k8s/
├── scripts/                    # 脚本
├── tests/                      # 测试
│   ├── integration/
│   └── e2e/
├── Makefile
├── go.mod
├── go.sum
└── README.md
```

---

## 3. 代码规范

### 3.1 命名规范

```go
// 包名: 小写单数
package user

// 接口名: 动词+er 或 名词+Interface
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
}

// 结构体名: 大写驼峰
type UserService struct {
    repo UserRepository
    log  *zap.Logger
}

// 变量名: 驼峰
userName := "john"
userID := "uuid"

// 常量名: 大写下划线
const (
    MaxRetryCount = 3
    DefaultTimeout = 30 * time.Second
)

// 错误变量: Err前缀
var (
    ErrUserNotFound = errors.New("user not found")
    ErrInvalidInput = errors.New("invalid input")
)

// 私有函数/方法: 小写驼峰
func (s *UserService) validateEmail(email string) error {
    return nil
}

// 公有函数/方法: 大写驼峰
func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    return nil, nil
}
```

### 3.2 错误处理

```go
// internal/pkg/errors/errors.go
package errors

import (
    "errors"
    "fmt"
)

// 应用错误类型
type AppError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
    Err     error  `json:"-"`
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// 错误构造函数
func New(code, message string) *AppError {
    return &AppError{Code: code, Message: message}
}

func Wrap(err error, code, message string) *AppError {
    return &AppError{Code: code, Message: message, Err: err}
}

// 预定义错误
var (
    ErrNotFound     = New("NOT_FOUND", "resource not found")
    ErrInvalidInput = New("INVALID_INPUT", "invalid input")
    ErrUnauthorized = New("UNAUTHORIZED", "unauthorized")
    ErrForbidden    = New("FORBIDDEN", "forbidden")
    ErrInternal     = New("INTERNAL_ERROR", "internal server error")
)

// 使用示例
func (r *UserRepository) GetByID(ctx context.Context, id string) (*User, error) {
    var user User
    if err := r.db.WithContext(ctx).First(&user, "id = ?", id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.Wrap(ErrNotFound, "USER_NOT_FOUND", "user not found")
        }
        return nil, errors.Wrap(err, "DB_ERROR", "database error")
    }
    return &user, nil
}
```

### 3.3 Context 使用

```go
// 必须将 context.Context 作为第一个参数
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    // 传递 context
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, err
    }
    return user, nil
}

// 设置超时
func (h *UserHandler) GetUser(c *gin.Context) {
    ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
    defer cancel()
    
    user, err := h.service.GetUser(ctx, c.Param("id"))
    if err != nil {
        handleError(c, err)
        return
    }
    
    c.JSON(http.StatusOK, user)
}

// 传递请求元数据
type contextKey string

const (
    UserIDKey    contextKey = "user_id"
    RequestIDKey contextKey = "request_id"
)

func WithUserID(ctx context.Context, userID string) context.Context {
    return context.WithValue(ctx, UserIDKey, userID)
}

func UserIDFromContext(ctx context.Context) (string, bool) {
    userID, ok := ctx.Value(UserIDKey).(string)
    return userID, ok
}
```

---

## 4. Web 框架规范

### 4.1 Gin 框架

```go
// cmd/api/main.go
package main

import (
    "log"
    
    "github.com/gin-gonic/gin"
    "go.uber.org/zap"
    
    "project/internal/config"
    "project/internal/handler"
    "project/internal/middleware"
    "project/internal/repository"
    "project/internal/service"
)

func main() {
    cfg := config.Load()
    
    logger, _ := zap.NewProduction()
    defer logger.Sync()
    
    // 数据库连接
    db, err := repository.NewDB(cfg.Database)
    if err != nil {
        log.Fatal(err)
    }
    
    // 依赖注入
    userRepo := repository.NewUserRepository(db)
    userService := service.NewUserService(userRepo, logger)
    userHandler := handler.NewUserHandler(userService)
    
    // 创建路由
    r := gin.New()
    
    // 全局中间件
    r.Use(middleware.Logger(logger))
    r.Use(middleware.Recovery(logger))
    r.Use(middleware.RequestID())
    r.Use(middleware.CORS())
    
    // 健康检查
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })
    
    // API v1
    v1 := r.Group("/api/v1")
    {
        users := v1.Group("/users")
        {
            users.GET("", userHandler.List)
            users.GET("/:id", userHandler.Get)
            users.POST("", userHandler.Create)
            users.PUT("/:id", userHandler.Update)
            users.DELETE("/:id", userHandler.Delete)
        }
    }
    
    if err := r.Run(":" + cfg.Server.Port); err != nil {
        log.Fatal(err)
    }
}
```

### 4.2 Handler 规范

```go
// internal/handler/user_handler.go
package handler

import (
    "net/http"
    
    "github.com/gin-gonic/gin"
    "github.com/go-playground/validator/v10"
    
    "project/internal/domain"
    "project/internal/service"
)

type UserHandler struct {
    service service.UserService
    validate *validator.Validate
}

func NewUserHandler(s service.UserService) *UserHandler {
    return &UserHandler{
        service: s,
        validate: validator.New(),
    }
}

// List godoc
// @Summary      List users
// @Description  get all users with pagination
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        page   query     int  false  "Page number"  default(1)
// @Param        size   query     int  false  "Page size"    default(10)
// @Success      200    {object}  PaginatedResponse{data=[]domain.User}
// @Router       /users [get]
func (h *UserHandler) List(c *gin.Context) {
    var req ListUsersRequest
    if err := c.ShouldBindQuery(&req); err != nil {
        c.JSON(http.StatusBadRequest, ErrorResponse(err))
        return
    }
    
    users, total, err := h.service.List(c.Request.Context(), req.Page, req.Size)
    if err != nil {
        handleError(c, err)
        return
    }
    
    c.JSON(http.StatusOK, PaginatedResponse{
        Data:  users,
        Total: total,
        Page:  req.Page,
        Size:  req.Size,
    })
}

// Create godoc
// @Summary      Create user
// @Description  create a new user
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        user  body      CreateUserRequest  true  "User info"
// @Success      201   {object}  domain.User
// @Router       /users [post]
func (h *UserHandler) Create(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, ErrorResponse(err))
        return
    }
    
    if err := h.validate.Struct(req); err != nil {
        c.JSON(http.StatusBadRequest, ValidationErrorResponse(err))
        return
    }
    
    user, err := h.service.Create(c.Request.Context(), &req)
    if err != nil {
        handleError(c, err)
        return
    }
    
    c.JSON(http.StatusCreated, user)
}

// 请求/响应结构
type ListUsersRequest struct {
    Page int `form:"page" binding:"min=1" default:"1"`
    Size int `form:"size" binding:"min=1,max=100" default:"10"`
}

type CreateUserRequest struct {
    Email    string `json:"email" binding:"required,email"`
    Name     string `json:"name" binding:"required,min=2,max=50"`
    Password string `json:"password" binding:"required,min=8"`
}

type PaginatedResponse struct {
    Data  interface{} `json:"data"`
    Total int64       `json:"total"`
    Page  int         `json:"page"`
    Size  int         `json:"size"`
}

func ErrorResponse(err error) gin.H {
    return gin.H{"error": err.Error()}
}

func ValidationErrorResponse(err error) gin.H {
    if validationErrors, ok := err.(validator.ValidationErrors); ok {
        errors := make(map[string]string)
        for _, e := range validationErrors {
            errors[e.Field()] = e.Tag()
        }
        return gin.H{"errors": errors}
    }
    return gin.H{"error": err.Error()}
}

func handleError(c *gin.Context, err error) {
    // 根据错误类型返回不同状态码
    switch {
    case errors.Is(err, ErrNotFound):
        c.JSON(http.StatusNotFound, ErrorResponse(err))
    case errors.Is(err, ErrInvalidInput):
        c.JSON(http.StatusBadRequest, ErrorResponse(err))
    case errors.Is(err, ErrUnauthorized):
        c.JSON(http.StatusUnauthorized, ErrorResponse(err))
    default:
        c.JSON(http.StatusInternalServerError, ErrorResponse(err))
    }
}
```

---

## 5. 数据库规范

### 5.1 GORM 使用

```go
// internal/repository/db.go
package repository

import (
    "fmt"
    "time"
    
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
    
    "project/internal/config"
    "project/internal/domain"
)

func NewDB(cfg config.DatabaseConfig) (*gorm.DB, error) {
    dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=%s",
        cfg.Host, cfg.User, cfg.Password, cfg.Name, cfg.Port, cfg.SSLMode)
    
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Silent),
        NowFunc: func() time.Time {
            return time.Now().UTC()
        },
    })
    if err != nil {
        return nil, err
    }
    
    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }
    
    // 连接池配置
    sqlDB.SetMaxOpenConns(cfg.MaxOpenConns)
    sqlDB.SetMaxIdleConns(cfg.MaxIdleConns)
    sqlDB.SetConnMaxLifetime(cfg.ConnMaxLifetime)
    
    // 自动迁移
    if cfg.AutoMigrate {
        if err := autoMigrate(db); err != nil {
            return nil, err
        }
    }
    
    return db, nil
}

func autoMigrate(db *gorm.DB) error {
    return db.AutoMigrate(
        &domain.User{},
        &domain.Order{},
    )
}

// internal/repository/user_repo.go
package repository

import (
    "context"
    
    "gorm.io/gorm"
    
    "project/internal/domain"
    "project/internal/pkg/errors"
)

type userRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) domain.UserRepository {
    return &userRepository{db: db}
}

func (r *userRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
    var user domain.User
    if err := r.db.WithContext(ctx).First(&user, "id = ?", id).Error; err != nil {
        if err == gorm.ErrRecordNotFound {
            return nil, errors.Wrap(errors.ErrNotFound, "USER_NOT_FOUND", "user not found")
        }
        return nil, errors.Wrap(err, "DB_ERROR", "database error")
    }
    return &user, nil
}

func (r *userRepository) List(ctx context.Context, page, size int) ([]*domain.User, int64, error) {
    var users []*domain.User
    var total int64
    
    query := r.db.WithContext(ctx).Model(&domain.User{})
    
    if err := query.Count(&total).Error; err != nil {
        return nil, 0, err
    }
    
    if err := query.Offset((page - 1) * size).Limit(size).Find(&users).Error; err != nil {
        return nil, 0, err
    }
    
    return users, total, nil
}

func (r *userRepository) Create(ctx context.Context, user *domain.User) error {
    return r.db.WithContext(ctx).Create(user).Error
}

func (r *userRepository) Update(ctx context.Context, user *domain.User) error {
    return r.db.WithContext(ctx).Save(user).Error
}

func (r *userRepository) Delete(ctx context.Context, id string) error {
    return r.db.WithContext(ctx).Delete(&domain.User{}, "id = ?", id).Error
}
```

---

## 6. 测试规范

### 6.1 单元测试

```go
// internal/service/user_service_test.go
package service

import (
    "context"
    "errors"
    "testing"
    
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "go.uber.org/zap"
    
    "project/internal/domain"
)

// Mock Repository
type mockUserRepository struct {
    mock.Mock
}

func (m *mockUserRepository) GetByID(ctx context.Context, id string) (*domain.User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*domain.User), args.Error(1)
}

func (m *mockUserRepository) Create(ctx context.Context, user *domain.User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}

func TestUserService_GetUser(t *testing.T) {
    logger := zap.NewNop()
    
    t.Run("success", func(t *testing.T) {
        mockRepo := new(mockUserRepository)
        service := NewUserService(mockRepo, logger)
        
        expectedUser := &domain.User{
            ID:    "123",
            Email: "test@example.com",
            Name:  "Test User",
        }
        
        mockRepo.On("GetByID", mock.Anything, "123").Return(expectedUser, nil)
        
        user, err := service.GetUser(context.Background(), "123")
        
        assert.NoError(t, err)
        assert.Equal(t, expectedUser, user)
        mockRepo.AssertExpectations(t)
    })
    
    t.Run("not found", func(t *testing.T) {
        mockRepo := new(mockUserRepository)
        service := NewUserService(mockRepo, logger)
        
        mockRepo.On("GetByID", mock.Anything, "999").Return(nil, errors.New("not found"))
        
        user, err := service.GetUser(context.Background(), "999")
        
        assert.Error(t, err)
        assert.Nil(t, user)
        mockRepo.AssertExpectations(t)
    })
}
```

### 6.2 集成测试

```go
// tests/integration/user_test.go
package integration

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"
    
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/suite"
    
    "project/internal/handler"
    "project/internal/repository"
    "project/internal/service"
)

type UserIntegrationTestSuite struct {
    suite.Suite
    router *gin.Engine
    db     *gorm.DB
}

func (s *UserIntegrationTestSuite) SetupSuite() {
    gin.SetMode(gin.TestMode)
    
    // 使用测试数据库
    db, err := repository.NewTestDB()
    if err != nil {
        s.T().Fatal(err)
    }
    s.db = db
    
    // 设置路由
    userRepo := repository.NewUserRepository(db)
    userService := service.NewUserService(userRepo, zap.NewNop())
    userHandler := handler.NewUserHandler(userService)
    
    r := gin.New()
    r.POST("/api/v1/users", userHandler.Create)
    r.GET("/api/v1/users/:id", userHandler.Get)
    
    s.router = r
}

func (s *UserIntegrationTestSuite) TearDownSuite() {
    // 清理测试数据
    sqlDB, _ := s.db.DB()
    sqlDB.Close()
}

func (s *UserIntegrationTestSuite) TestCreateUser() {
    req := handler.CreateUserRequest{
        Email:    "test@example.com",
        Name:     "Test User",
        Password: "password123",
    }
    
    body, _ := json.Marshal(req)
    w := httptest.NewRecorder()
    request, _ := http.NewRequest("POST", "/api/v1/users", bytes.NewBuffer(body))
    request.Header.Set("Content-Type", "application/json")
    
    s.router.ServeHTTP(w, request)
    
    assert.Equal(s.T(), http.StatusCreated, w.Code)
    
    var response domain.User
    err := json.Unmarshal(w.Body.Bytes(), &response)
    assert.NoError(s.T(), err)
    assert.Equal(s.T(), req.Email, response.Email)
    assert.Equal(s.T(), req.Name, response.Name)
}

func TestUserIntegration(t *testing.T) {
    suite.Run(t, new(UserIntegrationTestSuite))
}
```

---

## 7. 可观测性

### 7.1 日志 (Zap)

```go
// internal/pkg/logger/logger.go
package logger

import (
    "os"
    
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func New(env string) (*zap.Logger, error) {
    var config zap.Config
    
    if env == "production" {
        config = zap.NewProductionConfig()
        config.EncoderConfig.TimeKey = "timestamp"
        config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    } else {
        config = zap.NewDevelopmentConfig()
        config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
    }
    
    logger, err := config.Build(
        zap.AddCaller(),
        zap.AddCallerSkip(1),
    )
    if err != nil {
        return nil, err
    }
    
    return logger, nil
}

// 使用示例
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    s.log.Info("getting user",
        zap.String("user_id", id),
        zap.String("request_id", GetRequestID(ctx)),
    )
    
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        s.log.Error("failed to get user",
            zap.String("user_id", id),
            zap.Error(err),
        )
        return nil, err
    }
    
    s.log.Info("user found",
        zap.String("user_id", user.ID),
        zap.String("email", user.Email),
    )
    
    return user, nil
}
```

### 7.2 指标 (Prometheus)

```go
// internal/pkg/metrics/metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // HTTP请求指标
    HTTPRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    HTTPRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
    
    // 业务指标
    UsersCreatedTotal = promauto.NewCounter(
        prometheus.CounterOpts{
            Name: "users_created_total",
            Help: "Total number of users created",
        },
    )
)

// Gin中间件
func PrometheusMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        duration := time.Since(start).Seconds()
        status := strconv.Itoa(c.Writer.Status())
        
        HTTPRequestsTotal.WithLabelValues(
            c.Request.Method,
            c.FullPath(),
            status,
        ).Inc()
        
        HTTPRequestDuration.WithLabelValues(
            c.Request.Method,
            c.FullPath(),
        ).Observe(duration)
    }
}
```

### 7.3 追踪 (OpenTelemetry)

```go
// internal/pkg/tracer/tracer.go
package tracer

import (
    "context"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
    "go.opentelemetry.io/otel/trace"
)

func InitTracer(serviceName, endpoint string) (*sdktrace.TracerProvider, error) {
    ctx := context.Background()
    
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(endpoint),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }
    
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(serviceName),
        )),
    )
    
    otel.SetTracerProvider(tp)
    return tp, nil
}

// 使用示例
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "GetUser")
    defer span.End()
    
    span.SetAttributes(
        attribute.String("user.id", id),
    )
    
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        span.RecordError(err)
        return nil, err
    }
    
    return user, nil
}
```

---

## 8. AI Agent 集成

```go
// internal/agents/code_reviewer.go
package agents

import (
    "context"
    "encoding/json"
    "fmt"
    
    "github.com/your-org/ai-sdk-go"
)

type CodeReviewer struct {
    client *ai.Client
}

func NewCodeReviewer(apiKey string) *CodeReviewer {
    return &CodeReviewer{
        client: ai.NewClient(apiKey),
    }
}

type ReviewResult struct {
    Issues []Issue `json:"issues"`
    Score  int     `json:"score"`
}

type Issue struct {
    Line     int    `json:"line"`
    Severity string `json:"severity"`
    Message  string `json:"message"`
    Suggestion string `json:"suggestion"`
}

func (r *CodeReviewer) Review(ctx context.Context, filename, content string) (*ReviewResult, error) {
    prompt := fmt.Sprintf(`请审查以下Go代码，找出潜在问题:

文件名: %s

代码:
%s

请以JSON格式输出审查结果，包含issues数组和score分数。`, filename, content)
    
    response, err := r.client.Complete(ctx, prompt)
    if err != nil {
        return nil, err
    }
    
    var result ReviewResult
    if err := json.Unmarshal([]byte(response), &result); err != nil {
        return nil, err
    }
    
    return &result, nil
}
```

---

**参考**:
- [Effective Go](https://golang.org/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout)
- [Gin Documentation](https://gin-gonic.com/docs/)
- [GORM Documentation](https://gorm.io/docs/)
