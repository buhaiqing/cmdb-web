# CMDB 测试计划

## 1. 概述

### 1.1 目的

本文档描述 CMDB 系统的测试策略、测试范围和测试计划，确保系统质量符合要求。

### 1.2 测试范围

- 后端单元测试
- 后端集成测试
- 前端 E2E 测试
- API 测试
- 性能测试
- 安全测试

### 1.3 测试工具

| 测试类型 | 工具 | 说明 |
|----------|------|------|
| 单元测试 | pytest | Python 单元测试框架 |
| 集成测试 | pytest + TestClient | FastAPI 测试客户端 |
| E2E 测试 | Playwright | 端到端测试框架 |
| 覆盖率 | pytest-cov | 代码覆盖率统计 |
| API 测试 | 内置 Swagger UI | API 文档和测试 |

## 2. 测试策略

### 2.1 测试金字塔

```
           /\
          /  \      E2E 测试 (10%)
         /----\
        /      \   集成测试 (30%)
       /--------\
      /          \ 单元测试 (60%)
     /------------\
```

### 2.2 测试层次

#### 2.2.1 单元测试
- 测试单个函数或方法
- 模拟外部依赖
- 目标覆盖率 ≥ 80%

#### 2.2.2 集成测试
- 测试模块间交互
- 测试 API 端点
- 目标覆盖率 ≥ 70%

#### 2.2.3 E2E 测试
- 测试完整用户流程
- 使用真实浏览器
- 覆盖核心功能

## 3. 测试用例

### 3.1 认证模块测试

#### AUTH-001: 成功登录
```typescript
测试步骤:
1. 访问登录页面
2. 输入正确的用户名和密码
3. 点击登录按钮
预期结果:
- 登录成功
- 跳转到首页
- 显示用户信息
```

#### AUTH-002: 失败登录
```typescript
测试步骤:
1. 访问登录页面
2. 输入错误的用户名或密码
3. 点击登录按钮
预期结果:
- 登录失败
- 显示错误提示
- 停留在登录页
```

#### AUTH-003: 用户注册
```typescript
测试步骤:
1. 访问登录页面
2. 点击注册链接
3. 填写注册表单
4. 提交注册
预期结果:
- 注册成功
- 自动登录
- 跳转到首页
```

### 3.2 配置项管理测试

#### CI-001: 创建配置项
```typescript
测试步骤:
1. 登录系统
2. 导航到配置项列表
3. 点击新建按钮
4. 填写配置项信息
5. 提交创建
预期结果:
- 创建成功
- 显示在列表中
- 可以查看详情
```

#### CI-002: 编辑配置项
```typescript
测试步骤:
1. 在列表中选择一个配置项
2. 点击编辑按钮
3. 修改部分字段
4. 保存修改
预期结果:
- 保存成功
- 显示更新后的信息
```

#### CI-003: 搜索配置项
```typescript
测试步骤:
1. 在搜索框输入关键字
2. 选择过滤条件
3. 点击搜索按钮
预期结果:
- 显示匹配的列表
- 高亮关键字
```

#### CI-004: 删除配置项
```typescript
测试步骤:
1. 选择一个配置项
2. 点击删除按钮
3. 确认删除
预期结果:
- 删除成功
- 列表中不再显示
```

### 3.3 后端单元测试

#### test_security.py
```python
def test_password_hash():
    # 测试密码哈希功能
    assert verify_password(hash_password("test"), "test")

def test_verify_password_wrong():
    # 测试密码验证失败
    assert not verify_password(hash_password("test1"), "test2")
```

#### test_exceptions.py
```python
def test_resource_not_found():
    # 测试资源不存在异常
    with pytest.raises(ResourceNotFoundError):
        get_resource(999)
```

### 3.4 API 集成测试

```python
def test_get_ci_list(client, auth_headers):
    # 测试获取配置项列表
    response = client.get("/api/cis", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()["data"]

def test_create_ci(client, auth_headers):
    # 测试创建配置项
    response = client.post("/api/cis", json={
        "ci_type": "server",
        "name": "Test Server"
    }, headers=auth_headers)
    assert response.status_code == 201
```

## 4. 测试执行

### 4.1 后端测试

```bash
# 运行所有测试
cd backend
pytest

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 运行单元测试
pytest tests/unit

# 运行集成测试
pytest tests/integration
```

### 4.2 前端测试

```bash
# 运行所有 E2E 测试
cd frontend
npx playwright test

# UI 模式运行
npx playwright test --ui

# 生成 HTML 报告
npx playwright test --reporter=html
npx playwright show-report
```

### 4.3 测试报告

测试执行后生成以下报告：
- 代码覆盖率报告 (HTML)
- E2E 测试报告 (HTML)
- 测试结果总结

## 5. 测试数据

### 5.1 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | Admin@123 | 系统管理员 |
| operator | Operator@123 | 运维工程师 |
| viewer | Viewer@123 | 只读用户 |
| auditor | Auditor@123 | 审计员 |

### 5.2 测试数据准备

```python
# fixtures.py
@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("Test@123")
    )
    db_session.add(user)
    db_session.commit()
    return user
```

## 6. 质量门禁

### 6.1 代码覆盖率要求

| 测试类型 | 目标覆盖率 | 必需 |
|----------|------------|------|
| 单元测试 | ≥ 80% | 是 |
| 集成测试 | ≥ 70% | 是 |
| E2E 测试 | 核心功能 100% | 是 |

### 6.2 测试通过率要求

- 所有测试必须通过
- 无阻塞性 Bug
- 严重 Bug 已修复

### 6.3 性能要求

- API 响应时间 < 500ms
- 页面加载时间 < 3s
- 并发用户 ≥ 100

## 7. 持续集成

### 7.1 GitHub Actions 工作流

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 7.2 触发条件

- Push 到 main 分支
- 创建 Pull Request
- 定时执行（每日）

## 8. 缺陷管理

### 8.1 缺陷优先级

| 优先级 | 描述 | 响应时间 |
|--------|------|----------|
| P0 | 阻塞性缺陷 | 立即 |
| P1 | 严重缺陷 | 24 小时 |
| P2 | 一般缺陷 | 7 天 |
| P3 | 轻微缺陷 | 下个迭代 |

### 8.2 缺陷流程

```
发现 → 记录 → 分配 → 修复 → 验证 → 关闭
```

## 9. 附录

### 9.1 测试检查清单

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有 E2E 测试通过
- [ ] 代码覆盖率达标
- [ ] 性能测试通过
- [ ] 安全扫描通过
- [ ] 测试报告已生成

### 9.2 参考文档

- pytest 官方文档
- Playwright 官方文档
- Harness Engineering 测试最佳实践
