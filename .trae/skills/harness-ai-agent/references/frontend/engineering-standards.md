# 前端工程化规范 (2026 Edition)

> **标准**: React 19 + TypeScript 5.5 + Vite 6  
> **Harness 集成**: Feature Flags, A/B Testing, Real User Monitoring

---

## 1. 项目架构

### 1.1 目录结构
```
frontend/
├── src/
│   ├── app/                    # 应用入口
│   │   ├── layout.tsx          # 根布局
│   │   ├── page.tsx            # 首页
│   │   └── loading.tsx         # 加载状态
│   ├── components/             # 组件
│   │   ├── ui/                 # 基础 UI (shadcn/ui)
│   │   ├── forms/              # 表单组件
│   │   └── features/           # 业务组件
│   ├── hooks/                  # 自定义 Hooks
│   ├── lib/                    # 工具函数
│   ├── services/               # API 服务
│   ├── stores/                 # 状态管理 (Zustand)
│   └── types/                  # 类型定义
├── public/                     # 静态资源
├── .harness/                   # Harness 配置
├── e2e/                        # Playwright 测试
└── vite.config.ts
```

### 1.2 技术栈
| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | React | 19.x |
| 语言 | TypeScript | 5.5+ |
| 构建 | Vite | 6.x |
| 样式 | Tailwind CSS | 4.x |
| 状态 | Zustand | 5.x |
| 表单 | React Hook Form + Zod | latest |
| 测试 | Vitest + Playwright | latest |
| 监控 | Harness RUM | latest |

---

## 2. 代码规范

### 2.1 TypeScript 严格模式
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### 2.2 React 19 新特性使用
```typescript
// 使用 use() API 处理 Promise
import { use } from 'react';

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // 自动处理 Suspense
  return <div>{user.name}</div>;
}

// 使用 Server Components (如使用 Next.js)
// 默认所有组件为 Server Component
// 'use client' 仅用于需要浏览器 API 的组件
```

### 2.3 组件规范
```typescript
// components/features/UserCard.tsx
import { memo } from 'react';
import { z } from 'zod';

// Props 类型定义
const UserCardPropsSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  avatarUrl: z.string().url().optional(),
  onEdit: z.function().args(z.string()).returns(z.void()),
});

type UserCardProps = z.infer<typeof UserCardPropsSchema>;

// 组件实现
export const UserCard = memo(function UserCard({
  id,
  name,
  email,
  avatarUrl,
  onEdit,
}: UserCardProps) {
  return (
    <div className="rounded-lg border p-4">
      {avatarUrl && <img src={avatarUrl} alt={name} className="h-12 w-12 rounded-full" />}
      <h3 className="font-semibold">{name}</h3>
      <p className="text-sm text-gray-600">{email}</p>
      <button onClick={() => onEdit(id)}>编辑</button>
    </div>
  );
});
```

---

## 3. Harness Feature Flags 集成

### 3.1 Flag 定义
```typescript
// lib/harness-flags.ts
import { useFeatureFlag } from '@harnessio/ff-react-client-sdk';

export const FLAGS = {
  NEW_DASHBOARD: 'new_dashboard_v2',
  AI_ASSISTANT: 'ai_assistant_enabled',
  DARK_MODE: 'dark_mode_default',
} as const;

// Hook 封装
export function useNewDashboard() {
  return useFeatureFlag(FLAGS.NEW_DASHBOARD, false);
}

export function useAIAssistant() {
  return useFeatureFlag(FLAGS.AI_ASSISTANT, false);
}
```

### 3.2 组件中使用
```typescript
// components/features/Dashboard.tsx
import { useNewDashboard } from '@/lib/harness-flags';
import { DashboardV1 } from './DashboardV1';
import { DashboardV2 } from './DashboardV2';

export function Dashboard() {
  const isNewDashboard = useNewDashboard();
  
  return isNewDashboard ? <DashboardV2 /> : <DashboardV1 />;
}
```

---

## 4. 性能优化

### 4.1 代码分割
```typescript
// 路由级分割
import { lazy, Suspense } from 'react';

const AdminPanel = lazy(() => import('./AdminPanel'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <AdminPanel />
    </Suspense>
  );
}
```

### 4.2 资源优化
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
    // 启用压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
});
```

---

## 5. 测试策略

### 5.1 单元测试 (Vitest)
```typescript
// components/features/__tests__/UserCard.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { UserCard } from '../UserCard';

describe('UserCard', () => {
  it('renders user information correctly', () => {
    render(
      <UserCard
        id="123e4567-e89b-12d3-a456-426614174000"
        name="John Doe"
        email="john@example.com"
        onEdit={vi.fn()}
      />
    );
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
});
```

### 5.2 E2E 测试 (Playwright)
```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard loads with feature flag', async ({ page }) => {
  // 设置 Harness Feature Flag
  await page.goto('/dashboard?ff_new_dashboard_v2=true');
  
  await expect(page.getByTestId('dashboard-v2')).toBeVisible();
});
```

### 5.3 自动化测试友好性

#### 5.3.1 交互元素定位优化
- **test-data-id 属性**: 所有用户交互元素必须添加唯一的 `test-data-id` 属性
- **命名规范**: 遵循 "功能-组件-用途" 的命名规范，例如 `login-button-submit`
- **唯一性**: 确保 `test-data-id` 在整个应用范围内唯一

**示例实现**:
```tsx
// 推荐的实现方式
<button 
  test-data-id="login-button-submit"
  onClick={handleSubmit}
>
  登录
</button>

<input 
  test-data-id="user-input-email"
  type="email"
  value={email}
  onChange={handleEmailChange}
/>
```

#### 5.3.2 数组类组件标记系统
- **aria-labels 索引标记**: 对数组渲染的组件添加 `aria-label` 属性
- **索引规则**: 格式为 "组件名称-索引值"，索引从0开始连续编号
- **示例实现**:
```tsx
// 数组渲染的组件
users.map((user, index) => (
  <div 
    key={user.id}
    aria-label={`user-item-${index}`}
    test-data-id={`user-item-${user.id}`}
  >
    <span>{user.name}</span>
    <button 
      test-data-id={`user-button-edit-${user.id}`}
      onClick={() => editUser(user.id)}
    >
      编辑
    </button>
  </div>
));
```

#### 5.3.3 代码结构要求
- **清晰的层次结构**: 保持组件嵌套关系明确
- **容器边界**: 关键交互区域设置明确的容器边界
- **可测试性优先**: 在代码设计中优先考虑可测试性

#### 5.3.4 测试属性验证
- **自动化检查**: 集成自动化测试友好性检查机制
- **跨框架兼容**: 确保生成的代码能够通过主流测试框架的元素定位验证
- **测试属性文档**: 提供测试属性文档，说明各交互元素的 `test-data-id` 属性值及其对应功能

---

## 6. Harness RUM 集成

### 6.1 初始化
```typescript
// app/layout.tsx
import { HarnessRUM } from '@harnessio/rum-react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <HarnessRUM
          apiKey={process.env.NEXT_PUBLIC_HARNESS_RUM_KEY}
          serviceName="frontend-app"
          serviceVersion={process.env.NEXT_PUBLIC_APP_VERSION}
        />
        {children}
      </body>
    </html>
  );
}
```

### 6.2 自定义追踪
```typescript
// services/api.ts
import { trace } from '@harnessio/rum-react';

export async function fetchUser(id: string) {
  return trace('fetch-user', async () => {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  });
}
```

---

## 7. CI/CD 集成

### 7.1 Harness Pipeline 触发条件
- **PR 创建**: 运行 Lint + Unit Test
- **合并到 main**: 运行全量测试 + 构建 + 部署到 Staging
- **Tag 推送**: 生产发布

### 7.2 质量门禁
```yaml
# .harness/quality-gates.yml
gates:
  - name: test-coverage
    threshold: 80
    
  - name: lighthouse-score
    threshold:
      performance: 90
      accessibility: 95
      best-practices: 90
      seo: 90
      
  - name: bundle-size
    threshold:
      maxSize: "200kb"
      gzip: true
```

---

## 8. AI Agent 辅助规则

### 8.1 代码生成
- 生成组件时必须包含类型定义
- 使用 React 19 新特性 (use, Server Components)
- 自动添加 Harness Feature Flag 检查点

### 8.2 重构建议
- 识别重复代码并建议提取组件
- 检测性能瓶颈 (不必要的重渲染)
- 建议代码分割点

### 8.3 安全检查
- 检测 XSS 风险 (dangerouslySetInnerHTML)
- 检查敏感信息泄露
- 验证依赖漏洞 (npm audit)
