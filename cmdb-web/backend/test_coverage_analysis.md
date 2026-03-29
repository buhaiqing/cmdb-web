# 📊 后端测试覆盖率分析报告

## 🎯 总体概况

根据覆盖率报告，以下文件的测试覆盖率低于 90% 的目标阈值：

| 文件 | 覆盖率 | 缺失行数 | 严重程度 |
|------|--------|----------|----------|
| `app/middleware/auth.py` | **47%** | 43 行 | 🔴 严重 |
| `app/api/routes/user.py` | **56%** | 23 行 | 🔴 严重 |
| `app/api/routes/ci.py` | **55%** | 58 行 | 🔴 严重 |
| `app/main.py` | **81%** | 10 行 | 🟡 中等 |
| `app/models/base.py` | **86%** | 4 行 | 🟢 轻微 |

---

## 📝 详细分析

### 1. 🔴 app/middleware/auth.py (47%)

**文件功能**: JWT 认证中间件，负责请求的令牌验证和用户身份识别

#### 缺失覆盖的代码段分析：

##### ① 第 43-62 行：Token 提取和验证主逻辑
```python
# 获取 Token
token = self._extract_token(request)
if not token:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "未授权"},
    )

# 验证 Token
user_id = self._verify_token(token)
if not user_id:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "令牌无效或已过期"},
    )

# 将用户 ID 注入到请求状态中
request.state.user_id = user_id
request.state.token = token

return await call_next(request)
```

**功能类型**: **核心业务逻辑 + 错误处理**

**未覆盖场景**:
- ✅ 正常情况：提供有效 Token 的请求
- ❌ 边界条件：缺少 Authorization header 的情况
- ❌ 边界条件：Authorization header 格式错误的情况
- ❌ 错误处理：Token 无效或过期的情况

**风险等级**: 🔴 **高** - 这是安全关键代码，缺乏测试可能导致认证漏洞

---

##### ② 第 66-74 行：Token 提取逻辑
```python
def _extract_token(self, request: Request) -> Optional[str]:
    """从请求中提取 Token"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
```

**功能类型**: **输入验证 + 边界条件处理**

**未覆盖场景**:
- ❌ 边界条件：authorization 为 None
- ❌ 边界条件：authorization 为空字符串
- ❌ 边界条件：格式不是 "Bearer <token>"（如只有 "Bearer"）
- ❌ 边界条件：多个空格分隔的部分
- ❌ 边界条件：大小写 variations（如 "BEARER", "bearer"）

**风险等级**: 🟡 **中** - 输入验证逻辑需要全面测试

---

##### ③ 第 78-89 行：Token 验证逻辑
```python
def _verify_token(self, token: str) -> Optional[int]:
    """验证 Token 并返回用户 ID"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
        return int(user_id)
    except JWTError:
        return None
```

**功能类型**: **核心安全逻辑 + 异常处理**

**未覆盖场景**:
- ❌ 正常情况：使用有效 Token 验证成功
- ❌ 边界条件：Token 已过期
- ❌ 边界条件：Token 签名无效
- ❌ 边界条件：Token payload 中没有 "sub" 字段
- ❌ 边界条件："sub" 字段不是有效的整数
- ❌ 错误处理：JWTError 异常捕获

**风险等级**: 🔴 **高** - 安全核心逻辑，必须全面测试

---

### 2. 🔴 app/api/routes/user.py (56%)

**文件功能**: 用户管理相关的 API 路由

#### 缺失覆盖的代码段分析：

##### ① 第 32-38 行：用户列表查询
```python
def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取用户列表"""
    user_service = UserService(db)
    skip = (page - 1) * page_size

    items = user_service.get_multi(skip=skip, limit=page_size)
    total = user_service.get_count()

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：第一页查询
- ❌ 边界条件：页码边界值（page=1, page 很大）
- ❌ 边界条件：每页大小边界值（page_size=1, page_size=100）
- ❌ 边界条件：空结果集

**风险等级**: 🟡 **中** - 基础 CRUD 操作，影响分页功能

---

##### ② 第 53-54 行：创建用户
```python
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """创建用户"""
    user_service = UserService(db)
    return user_service.create(user_in=user_in)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：创建成功
- ❌ 边界条件：用户名冲突（服务层会抛 ConflictException）
- ❌ 边界条件：邮箱冲突
- ❌ 边界条件：无效的用户数据

**风险等级**: 🟡 **中** - 用户管理核心功能

---

##### ③ 第 64-68 行：获取单个用户
```python
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取用户详情"""
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException(message="用户不存在")
    return user
```

**功能类型**: **主要业务逻辑 + 错误处理**

**未覆盖场景**:
- ❌ 正常情况：用户存在
- ❌ 边界条件：用户不存在（抛出 NotFoundException）
- ❌ 边界条件：user_id 为负数或 0

**风险等级**: 🟡 **中** - 基础查询功能

---

##### ④ 第 79-80 行：更新用户
```python
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """更新用户"""
    user_service = UserService(db)
    return user_service.update(user_id=user_id, user_in=user_in)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：更新成功
- ❌ 边界条件：用户不存在
- ❌ 边界条件：邮箱被其他用户使用
- ❌ 边界条件：密码更新

**风险等级**: 🟡 **中** - 用户数据修改功能

---

##### ⑤ 第 90-91 行：删除用户
```python
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """删除用户"""
    user_service = UserService(db)
    user_service.delete(user_id=user_id)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：删除成功
- ❌ 边界条件：用户不存在
- ❌ 边界条件：删除自己的账号

**风险等级**: 🟡 **中** - 数据删除操作

---

### 3. 🔴 app/api/routes/ci.py (55%)

**文件功能**: 配置项（CI）管理相关的 API 路由

#### 缺失覆盖的代码段分析：

##### ① 第 35-47 行：CI 列表查询
```python
@router.get("", response_model=PaginatedResponse[CIResponse])
def list_cis(...):
    """获取配置项列表"""
    service = CIService(db)
    skip = (page - 1) * page_size

    items = service.get_multi(
        skip=skip,
        limit=page_size,
        ci_type=ci_type,
        status=status,
        environment=environment,
    )
    total = service.get_count(ci_type=ci_type, status=status, environment=environment)

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
```

**功能类型**: **主要业务逻辑 + 查询过滤**

**未覆盖场景**:
- ❌ 各种过滤条件组合（ci_type, status, environment）
- ❌ 边界条件：无过滤条件
- ❌ 边界条件：所有过滤条件同时使用
- ❌ 边界条件：空结果集

**风险等级**: 🟡 **中** - CMDB 核心查询功能

---

##### ② 第 79-83 行：获取单个 CI
```python
@router.get("/{ci_id}", response_model=CIResponse)
def get_ci(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """获取配置项详情"""
    service = CIService(db)
    ci = service.get_by_id(ci_id)
    if not ci:
        raise NotFoundException(message="配置项不存在")
    return ci
```

**功能类型**: **主要业务逻辑 + 错误处理**

**未覆盖场景**:
- ❌ 正常情况：CI 存在
- ❌ 边界条件：CI 不存在

**风险等级**: 🟡 **中** - 基础查询功能

---

##### ③ 第 93-94 行：更新 CI
```python
@router.put("/{ci_id}", response_model=CIResponse)
def update_ci(
    ci_id: int,
    ci_in: CIUpdate,
    db: Session = Depends(get_db),
):
    """更新配置项"""
    service = CIService(db)
    return service.update(ci_id=ci_id, ci_in=ci_in)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：更新成功
- ❌ 边界条件：CI 不存在
- ❌ 边界条件：部分字段更新

**风险等级**: 🟡 **中** - 配置项修改功能

---

##### ④ 第 103-104 行：删除 CI
```python
@router.delete("/{ci_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ci(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """删除配置项"""
    service = CIService(db)
    service.delete(ci_id=ci_id)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：删除成功
- ❌ 边界条件：CI 不存在
- ❌ 边界条件：CI 有关联关系时的删除

**风险等级**: 🟡 **中** - 数据删除操作

---

##### ⑤ 第 114-119 行：创建 CI 关系
```python
@router.post("/{ci_id}/relations", response_model=CIRelationResponse)
def create_relation(
    ci_id: int,
    relation_in: CIRelationCreate,
    db: Session = Depends(get_db),
):
    """创建配置项关系"""
    service = CIService(db)
    # 强制设置源配置项为当前 ci_id
    relation_data = relation_in.model_dump()
    relation_data["source_ci_id"] = ci_id
    relation_update = CIRelationCreate(**relation_data)
    return service.create_relation(relation_in=relation_update)
```

**功能类型**: **主要业务逻辑 + 数据转换**

**未覆盖场景**:
- ❌ 正常情况：关系创建成功
- ❌ 边界条件：源 CI 不存在
- ❌ 边界条件：目标 CI 不存在
- ❌ 边界条件：关系已存在

**风险等级**: 🟡 **中** - CMDB 关系管理核心功能

---

##### ⑥ 第 128-129 行：获取 CI 关系
```python
@router.get("/{ci_id}/relations", response_model=List[CIRelationResponse])
def get_relations(
    ci_id: int,
    db: Session = Depends(get_db),
):
    """获取配置项的所有关系"""
    service = CIService(db)
    return service.get_relations(ci_id=ci_id)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：有关系
- ❌ 边界条件：没有关系
- ❌ 边界条件：CI 不存在

**风险等级**: 🟢 **低** - 查询功能

---

##### ⑦ 第 138-139 行：删除 CI 关系
```python
@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(
    relation_id: int,
    db: Session = Depends(get_db),
):
    """删除配置项关系"""
    service = CIService(db)
    service.delete_relation(relation_id=relation_id)
```

**功能类型**: **主要业务逻辑**

**未覆盖场景**:
- ❌ 正常情况：删除成功
- ❌ 边界条件：关系不存在

**风险等级**: 🟢 **低** - 关系删除操作

---

##### ⑧ 第 148-162 行：搜索 CI
```python
@router.post("/search", response_model=PaginatedResponse[CIResponse])
def search_cis(
    search_request: CISearchRequest,
    db: Session = Depends(get_db),
):
    """搜索配置项"""
    service = CIService(db)
    skip = (search_request.page - 1) * search_request.page_size

    items, total = service.search(
        ci_type=search_request.ci_type,
        name=search_request.name,
        code=search_request.code,
        status=search_request.status,
        environment=search_request.environment,
        owner=search_request.owner,
        skip=skip,
        limit=search_request.page_size,
    )

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
    )
```

**功能类型**: **主要业务逻辑 + 复杂查询**

**未覆盖场景**:
- ❌ 各种搜索条件组合
- ❌ 模糊匹配（name, code, owner 使用 ilike）
- ❌ 分页参数边界值
- ❌ 空搜索结果

**风险等级**: 🟡 **中** - 高级搜索功能

---

### 4. 🟡 app/main.py (81%)

**文件功能**: FastAPI 应用主入口和配置

#### 缺失覆盖的代码段分析：

##### ① 第 35-40 行：应用生命周期关闭逻辑
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行的操作
    logger.info("Starting CMDB API...")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")

    # 初始化数据库
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

    yield

    # 关闭时执行的操作
    logger.info("Shutting down CMDB API...")  # ← 未覆盖
```

**功能类型**: **应用生命周期管理**

**未覆盖场景**:
- ❌ 应用优雅关闭时的日志记录

**风险等级**: 🟢 **低** - 仅日志记录，不影响功能

---

##### ② 第 85 行：根路径端点
```python
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to CMDB API",
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
```

**功能类型**: **健康检查/信息端点**

**未覆盖场景**:
- ❌ GET / 请求

**风险等级**: 🟢 **低** - 信息展示端点

---

##### ③ 第 96 行：健康检查端点
```python
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.APP_VERSION}
```

**功能类型**: **健康检查端点**

**未覆盖场景**:
- ❌ GET /health 请求

**风险等级**: 🟢 **低** - 运维监控端点

---

##### ④ 第 100-102 行：直接运行入口
```python
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
```

**功能类型**: **开发环境启动代码**

**未覆盖场景**:
- ❌ 直接 python app/main.py 运行

**风险等级**: 🟢 **低** - 通常通过 uvicorn/gunicorn 启动，不直接运行

---

### 5. 🟢 app/models/base.py (86%)

**文件功能**: SQLAlchemy 模型基类定义

#### 缺失覆盖的代码段分析：

##### ① 第 16-19 行：表名自动生成逻辑
```python
@declared_attr
def __tablename__(cls) -> str:
    # 将驼峰命名转换为下划线命名
    import re

    name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
    return f"t_{name}"
```

**功能类型**: **元编程/工具方法**

**未覆盖场景**:
- ❌ 各种驼峰命名转换（如 UserProfile → t_user_profile）
- ❌ 全大写字母的处理
- ❌ 连续大写字母的处理

**风险等级**: 🟢 **低** - 正则表达式逻辑简单，已在实际使用中验证

---

## 🎯 测试补充优先级建议

### 优先级排序矩阵

| 优先级 | 文件 | 理由 | 预计工作量 |
|--------|------|------|-----------|
| **P0 - 最高** | `app/middleware/auth.py` | 🔴 安全关键代码，认证是系统第一道防线 | 4-6 小时 |
| **P1 - 高** | `app/api/routes/user.py` | 🔴 用户管理核心功能，涉及敏感数据 | 3-4 小时 |
| **P1 - 高** | `app/api/routes/ci.py` | 🔴 CMDB 核心业务逻辑，配置项管理 | 5-7 小时 |
| **P2 - 中** | `app/main.py` | 🟡 应用入口，影响部署和监控 | 1-2 小时 |
| **P3 - 低** | `app/models/base.py` | 🟢 基础工具类，风险较低 | 0.5-1 小时 |

---

## 📋 具体测试补充建议

### P0: app/middleware/auth.py

**建议测试文件**: `tests/middleware/test_auth.py`

**必测场景**:

```python
# 1. 认证成功场景
def test_auth_success_with_valid_token():
    """测试有效 Token 的认证成功"""
    
# 2. Token 缺失场景
def test_auth_missing_token():
    """测试缺少 Authorization header"""
    
def test_auth_empty_authorization():
    """测试空 Authorization header"""
    
# 3. Token 格式错误场景
def test_auth_invalid_format():
    """测试非 Bearer 格式"""
    
def test_auth_only_bearer_keyword():
    """测试只有 'Bearer' 没有 token"""
    
# 4. Token 无效场景
def test_auth_expired_token():
    """测试过期 Token"""
    
def test_auth_invalid_signature():
    """测试签名无效的 Token"""
    
def test_auth_token_without_sub():
    """测试 payload 中没有 sub 字段的 Token"""
    
def test_auth_token_invalid_sub():
    """测试 sub 字段不是整数的 Token"""
    
# 5. 排除路径场景
def test_auth_excluded_paths():
    """测试排除认证的路径（/api/auth/login, /docs 等）"""
```

**关键测试点**:
- ✅ Mock JWT 解码过程
- ✅ 测试各种边界条件
- ✅ 验证 request.state 正确注入 user_id 和 token
- ✅ 验证返回的 JSONResponse 状态码和内容

---

### P1: app/api/routes/user.py

**建议测试文件**: `tests/api/routes/test_user.py`

**必测场景**:

```python
# 1. 列表查询
def test_list_users_page_1():
    """测试第一页查询"""
    
def test_list_users_pagination():
    """测试分页参数边界值"""
    
def test_list_users_empty_result():
    """测试空结果集"""
    
# 2. 创建用户
def test_create_user_success():
    """测试创建成功"""
    
def test_create_user_duplicate_username():
    """测试用户名冲突"""
    
def test_create_user_duplicate_email():
    """测试邮箱冲突"""
    
# 3. 获取用户
def test_get_user_success():
    """测试获取成功"""
    
def test_get_user_not_found():
    """测试用户不存在"""
    
# 4. 更新用户
def test_update_user_success():
    """测试更新成功"""
    
def test_update_user_not_found():
    """测试用户不存在"""
    
def test_update_user_email_conflict():
    """测试邮箱被其他用户使用"""
    
def test_update_user_password():
    """测试密码更新（应加密存储）"""
    
# 5. 删除用户
def test_delete_user_success():
    """测试删除成功"""
    
def test_delete_user_not_found():
    """测试用户不存在"""
```

**关键测试点**:
- ✅ Mock get_current_user 依赖
- ✅ 测试分页逻辑
- ✅ 测试异常抛出（ConflictException, NotFoundException）
- ✅ 验证密码加密存储

---

### P1: app/api/routes/ci.py

**建议测试文件**: `tests/api/routes/test_ci.py`

**必测场景**:

```python
# 1. 列表查询（带过滤）
def test_list_cis_no_filters():
    """测试无过滤条件"""
    
def test_list_cis_with_type_filter():
    """测试按类型过滤"""
    
def test_list_cis_with_status_filter():
    """测试按状态过滤"""
    
def test_list_cis_with_environment_filter():
    """测试按环境过滤"""
    
def test_list_cis_all_filters():
    """测试所有过滤条件组合"""
    
# 2. 获取 CI
def test_get_ci_success():
    """测试获取成功"""
    
def test_get_ci_not_found():
    """测试 CI 不存在"""
    
# 3. 更新 CI
def test_update_ci_success():
    """测试更新成功"""
    
def test_update_ci_not_found():
    """测试 CI 不存在"""
    
def test_update_ci_partial_fields():
    """测试部分字段更新"""
    
# 4. 删除 CI
def test_delete_ci_success():
    """测试删除成功"""
    
def test_delete_ci_not_found():
    """测试 CI 不存在"""
    
# 5. CI 关系
def test_create_relation_success():
    """测试创建关系成功"""
    
def test_create_relation_source_not_found():
    """测试源 CI 不存在"""
    
def test_create_relation_target_not_found():
    """测试目标 CI 不存在"""
    
def test_create_relation_duplicate():
    """测试关系已存在"""
    
def test_get_relations_success():
    """测试获取关系列表"""
    
def test_get_relations_empty():
    """测试没有关系"""
    
def test_delete_relation_success():
    """测试删除关系成功"""
    
# 6. 搜索 CI
def test_search_cis_by_name():
    """测试按名称模糊搜索"""
    
def test_search_cis_by_code():
    """测试按代码模糊搜索"""
    
def test_search_cis_by_owner():
    """测试按负责人模糊搜索"""
    
def test_search_cis_combined_filters():
    """测试组合搜索条件"""
    
def test_search_cis_empty_result():
    """测试空搜索结果"""
```

**关键测试点**:
- ✅ Mock CIService 方法
- ✅ 测试各种过滤条件组合
- ✅ 测试模糊查询（ilike）
- ✅ 测试关系管理的完整性
- ✅ 测试分页逻辑

---

### P2: app/main.py

**建议测试文件**: `tests/test_main.py`

**必测场景**:

```python
def test_root_endpoint():
    """测试根路径端点"""
    
def test_health_check_endpoint():
    """测试健康检查端点"""
    
def test_lifespan_startup():
    """测试应用启动时的日志和数据库初始化"""
    
def test_lifespan_shutdown():
    """测试应用关闭时的日志"""
```

**关键测试点**:
- ✅ 使用 TestClient 测试端点
- ✅ 验证返回的 JSON 结构
- ✅ 可以使用 caplog 验证日志输出

---

### P3: app/models/base.py

**建议测试文件**: `tests/models/test_base.py`

**必测场景**:

```python
def test_tablename_generation_simple():
    """测试简单驼峰命名转换 (UserProfile → t_user_profile)"""
    
def test_tablename_generation_consecutive_caps():
    """测试连续大写 (XMLParser → t_xml_parser)"""
    
def test_to_dict_with_datetime():
    """测试 datetime 字段转换为 ISO 字符串"""
    
def test_to_dict_with_regular_fields():
    """测试普通字段转换"""
```

**关键测试点**:
- ✅ 创建测试模型验证表名生成
- ✅ 验证 datetime 序列化
- ✅ 验证普通字段序列化

---

## 📊 预期覆盖率提升

完成上述测试补充后，预期覆盖率提升：

| 文件 | 当前覆盖率 | 目标覆盖率 | 提升幅度 |
|------|-----------|-----------|---------|
| auth.py | 47% | 95%+ | +48% |
| user.py | 56% | 95%+ | +39% |
| ci.py | 55% | 95%+ | +40% |
| main.py | 81% | 100% | +19% |
| base.py | 86% | 100% | +14% |

**整体预期提升**: 从当前平均 ~65% 提升至 **95%+**

---

## 🎓 总结建议

### 立即行动（本周）
1. ✅ **优先补充 auth.py 的测试** - 安全无小事
2. ✅ **补充 user.py 的基础 CRUD 测试** - 用户管理是核心功能

### 短期计划（下周）
3. ✅ **补充 ci.py 的完整测试** - CMDB 业务核心
4. ✅ **补充 main.py 的端点测试** - 完善度提升

### 长期优化（本月）
5. ✅ **补充 base.py 的工具方法测试** - 完善最后一块拼图
6. ✅ **建立覆盖率门禁** - PR 合并前检查覆盖率不低于 90%

### 质量改进建议
- 📌 在 CI/CD 中集成覆盖率检查
- 📌 对新代码实施更严格的覆盖率要求
- 📌 定期审查测试质量，避免"为了覆盖率而测试"
- 📌 考虑引入 mutation testing 验证测试有效性

---

**报告生成时间**: 2026-03-29  
**分析工具**: pytest-cov 覆盖率报告  
**目标标准**: 覆盖率 ≥ 90%
