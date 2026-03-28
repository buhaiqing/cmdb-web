import { test as base } from '@playwright/test'
import { http, HttpResponse, delay, passthrough } from 'msw'
import { setupServer } from 'msw/node'

export { handlers } from './mock-handlers'

const mockUsers = [
  {
    id: '1',
    username: 'admin',
    password: 'admin123',
    name: '管理员',
    email: 'admin@example.com',
    role: 'admin',
  },
  {
    id: '2',
    username: 'user',
    password: 'user123',
    name: '普通用户',
    email: 'user@example.com',
    role: 'user',
  },
]

// Mock 配置项数据 - 使用可变数组以便在测试中动态修改
let mockCIs = [
  {
    id: '1',
    name: 'Web 服务器 1',
    code: 'WEB-SRV-001',
    type: 'server',
    status: 'online',
    description: '主 Web 服务器',
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T10:00:00Z',
  },
  {
    id: '2',
    name: '数据库服务器',
    code: 'DB-SRV-001',
    type: 'database',
    status: 'online',
    description: '主数据库服务器',
    createdAt: '2024-01-02T10:00:00Z',
    updatedAt: '2024-01-02T10:00:00Z',
  },
  {
    id: '3',
    name: '应用服务器',
    code: 'APP-SRV-001',
    type: 'application',
    status: 'offline',
    description: '应用服务器',
    createdAt: '2024-01-03T10:00:00Z',
    updatedAt: '2024-01-03T10:00:00Z',
  },
  {
    id: '4',
    name: '缓存服务器',
    code: 'CACHE-SRV-001',
    type: 'cache',
    status: 'online',
    description: 'Redis 缓存服务器',
    createdAt: '2024-01-04T10:00:00Z',
    updatedAt: '2024-01-04T10:00:00Z',
  },
  {
    id: '5',
    name: '消息队列',
    code: 'MQ-001',
    type: 'middleware',
    status: 'online',
    description: 'RabbitMQ 消息队列',
    createdAt: '2024-01-05T10:00:00Z',
    updatedAt: '2024-01-05T10:00:00Z',
  },
]

// 创建 Mock Server
const createHandlers = () => [
  // 认证相关 API - 前端使用 /api 作为 base URL
  http.post('http://localhost:3000/api/auth/login', async ({ request }) => {
    await delay(300)

    // 前端使用 form-data 格式
    const formData = await request.formData()
    const username = formData.get('username') as string
    const password = formData.get('password') as string

    const user = mockUsers.find(u => u.username === username && u.password === password)

    if (user) {
      return HttpResponse.json({
        success: true,
        message: '登录成功',
        data: {
          access_token: 'mock-jwt-token-' + user.id,
          token_type: 'Bearer',
          expires_in: 3600,
        },
      })
    }

    return HttpResponse.json({
      success: false,
      error: {
        code: 'INVALID_CREDENTIALS',
        message: '用户名或密码错误',
      },
    }, { status: 401 })
  }),

  http.post('http://localhost:3000/api/auth/logout', async () => {
    await delay(200)
    return HttpResponse.json({
      success: true,
      message: '登出成功',
    })
  }),

  http.get('http://localhost:3000/api/auth/me', async () => {
    await delay(200)
    return HttpResponse.json({
      success: true,
      message: '获取用户信息成功',
      data: {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        full_name: '管理员',
        status: 'active' as const,
        is_superuser: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    })
  }),

  // 配置项相关 API
  http.get('http://localhost:3000/api/cis', async ({ request }) => {
    await delay(300)

    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const page_size = parseInt(url.searchParams.get('page_size') || '10')
    const name = url.searchParams.get('name') || ''
    const type = url.searchParams.get('type') || ''
    const status = url.searchParams.get('status') || ''

    // 过滤数据
    let filteredCIs = [...mockCIs].filter(ci => {
      if (name && !ci.name.toLowerCase().includes(name.toLowerCase())) return false
      if (type && ci.type !== type) return false
      if (status && ci.status !== status) return false
      return true
    })

    const total = filteredCIs.length
    const start = (page - 1) * page_size
    const end = start + page_size
    const items = filteredCIs.slice(start, end)

    return HttpResponse.json({
      success: true,
      message: '获取配置项列表成功',
      data: {
        items,
        total,
        page,
        page_size,
      },
    })
  }),

  http.get('http://localhost:3000/api/cis/:id', async ({ params }) => {
    await delay(200)

    const { id } = params
    const ci = mockCIs.find(c => c.id === id)

    if (ci) {
      return HttpResponse.json({
        success: true,
        message: '获取配置项成功',
        data: ci,
      })
    }

    return HttpResponse.json({
      success: false,
      error: {
        code: 'NOT_FOUND',
        message: '配置项不存在',
      },
    }, { status: 404 })
  }),

  http.post('http://localhost:3000/api/cis', async ({ request }) => {
    await delay(300)

    const body = await request.json() as { name: string; code: string; type: string; status: string; description?: string }
    const newCI = {
      id: String(mockCIs.length + 1),
      ...body,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    mockCIs.push(newCI)

    return HttpResponse.json({
      success: true,
      message: '创建成功',
      data: newCI,
    }, { status: 201 })
  }),

  http.put('http://localhost:3000/api/cis/:id', async ({ params, request }) => {
    await delay(300)

    const { id } = params
    const index = mockCIs.findIndex(c => c.id === id)

    if (index !== -1) {
      const body = await request.json()
      mockCIs[index] = {
        ...mockCIs[index],
        ...body,
        updatedAt: new Date().toISOString(),
      }

      return HttpResponse.json({
        success: true,
        message: '更新成功',
        data: mockCIs[index],
      })
    }

    return HttpResponse.json({
      success: false,
      error: {
        code: 'NOT_FOUND',
        message: '配置项不存在',
      },
    }, { status: 404 })
  }),

  http.delete('http://localhost:3000/api/cis/:id', async ({ params }) => {
    await delay(300)

    const { id } = params
    const index = mockCIs.findIndex(c => c.id === id)

    if (index !== -1) {
      mockCIs.splice(index, 1)

      return HttpResponse.json({
        success: true,
        message: '删除成功',
      })
    }

    return HttpResponse.json({
      success: false,
      error: {
        code: 'NOT_FOUND',
        message: '配置项不存在',
      },
    }, { status: 404 })
  }),

  // 用户相关 API
  http.get('http://localhost:3000/api/users', async () => {
    await delay(200)

    return HttpResponse.json({
      success: true,
      message: '获取用户列表成功',
      data: {
        items: mockUsers.map(({ password, ...user }) => ({
          ...user,
          id: parseInt(user.id),
          status: 'active' as const,
          is_superuser: user.role === 'admin',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        })),
        total: mockUsers.length,
        page: 1,
        page_size: 10,
      },
    })
  }),

  // 放行所有前端静态资源请求
  http.get<{ path: string }>('http://localhost:3000/*path', () => {
    return passthrough()
  }),
  http.post<{ path: string }>('http://localhost:3000/*path', () => {
    return passthrough()
  }),
]

// 扩展 Playwright 的 test 对象，提供 mockServer 功能
export const test = base.extend<{
  mockServer: {
    resetHandlers: () => void
    use: (handlers: any[]) => void
  }
}>({
  mockServer: async ({}, use) => {
    const server = setupServer(...createHandlers())
    
    // 启动服务器
    server.listen({ onUnhandledRequest: 'bypass' })
    
    await use({
      resetHandlers: () => {
        server.resetHandlers()
      },
      use: (handlers: any[]) => {
        server.use(...handlers)
      },
    })
    
    // 清理
    server.close()
  },
})

export { expect } from '@playwright/test'
