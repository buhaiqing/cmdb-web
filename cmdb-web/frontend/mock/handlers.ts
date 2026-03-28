import { http, HttpResponse, delay } from 'msw'

// Mock 用户数据
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

// Mock 配置项数据 - 使用 let 以便可以修改
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

export const handlers = [
  // 认证相关 API - 前端请求的是 /api/auth/login（baseURL: '/api'）
  http.post('/api/auth/login', async ({ request }) => {
    await delay(300) // 模拟网络延迟
    
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
      message: '用户名或密码错误',
      error: {
        code: 'INVALID_CREDENTIALS',
        message: '用户名或密码错误',
      },
    }, { status: 401 })
  }),

  http.post('/api/auth/logout', async () => {
    await delay(200)
    return HttpResponse.json({
      success: true,
      message: '登出成功',
    })
  }),

  // 配置项相关 API
  http.get('/api/cis', async ({ request }) => {
    await delay(300)
    
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10')
    const name = url.searchParams.get('name') || ''
    const type = url.searchParams.get('type') || ''
    const status = url.searchParams.get('status') || ''
    
    // 过滤数据
    let filteredCIs = mockCIs.filter(ci => {
      if (name && !ci.name.toLowerCase().includes(name.toLowerCase())) return false
      if (type && ci.type !== type) return false
      if (status && ci.status !== status) return false
      return true
    })
    
    const total = filteredCIs.length
    const start = (page - 1) * pageSize
    const end = start + pageSize
    const data = filteredCIs.slice(start, end)
    
    return HttpResponse.json({
      success: true,
      data: {
        list: data,
        total,
        page,
        pageSize,
      },
    })
  }),

  http.get('/api/cis/:id', async ({ params }) => {
    await delay(200)
    
    const { id } = params
    const ci = mockCIs.find(c => c.id === id)
    
    if (ci) {
      return HttpResponse.json({
        success: true,
        data: ci,
      })
    }
    
    return HttpResponse.json({
      success: false,
      message: '配置项不存在',
    }, { status: 404 })
  }),

  http.post('/api/cis', async ({ request }) => {
    await delay(300)
    
    const body = await request.json() as Record<string, unknown>
    const newCI = {
      id: String(mockCIs.length + 1),
      name: body.name as string,
      code: body.code as string,
      type: body.type as string,
      status: body.status as string,
      description: (body.description as string) || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    
    mockCIs.push(newCI)
    
    return HttpResponse.json({
      success: true,
      data: newCI,
      message: '创建成功',
    }, { status: 201 })
  }),

  http.put('/api/cis/:id', async ({ params, request }) => {
    await delay(300)
    
    const { id } = params
    const index = mockCIs.findIndex(c => c.id === id)
    
    if (index !== -1) {
      const body = await request.json() as Record<string, unknown>
      mockCIs[index] = {
        ...mockCIs[index],
        name: (body.name as string) || mockCIs[index].name,
        code: (body.code as string) || mockCIs[index].code,
        type: (body.type as string) || mockCIs[index].type,
        status: (body.status as string) || mockCIs[index].status,
        description: (body.description as string) || mockCIs[index].description,
        updatedAt: new Date().toISOString(),
      }
      
      return HttpResponse.json({
        success: true,
        data: mockCIs[index],
        message: '更新成功',
      })
    }
    
    return HttpResponse.json({
      success: false,
      message: '配置项不存在',
    }, { status: 404 })
  }),

  http.delete('/api/cis/:id', async ({ params }) => {
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
      message: '配置项不存在',
    }, { status: 404 })
  }),

  // 用户相关 API
  http.get('/api/users', async () => {
    await delay(200)
    
    return HttpResponse.json({
      success: true,
      data: {
        list: mockUsers.map(({ password, ...user }) => user),
        total: mockUsers.length,
      },
    })
  }),
]
