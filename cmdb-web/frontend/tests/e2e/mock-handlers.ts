import { http, HttpResponse, delay, passthrough } from 'msw'

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

let mockCIs = [
  {
    id: '1',
    name: 'Web 服务器 1',
    code: 'WEB-SRV-001',
    ci_type: 'server',
    status: 'online',
    description: '主 Web 服务器',
    environment: 'production',
    owner: 'admin',
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T10:00:00Z',
  },
  {
    id: '2',
    name: '数据库服务器',
    code: 'DB-SRV-001',
    ci_type: 'database',
    status: 'online',
    description: '主数据库服务器',
    environment: 'production',
    owner: 'admin',
    createdAt: '2024-01-02T10:00:00Z',
    updatedAt: '2024-01-02T10:00:00Z',
  },
  {
    id: '3',
    name: '应用服务器',
    code: 'APP-SRV-001',
    ci_type: 'application',
    status: 'offline',
    description: '应用服务器',
    environment: 'int',
    owner: 'user',
    createdAt: '2024-01-03T10:00:00Z',
    updatedAt: '2024-01-03T10:00:00Z',
  },
  {
    id: '4',
    name: '缓存服务器',
    code: 'CACHE-SRV-001',
    ci_type: 'middleware',
    status: 'online',
    description: 'Redis 缓存服务器',
    environment: 'production',
    owner: 'admin',
    createdAt: '2024-01-04T10:00:00Z',
    updatedAt: '2024-01-04T10:00:00Z',
  },
  {
    id: '5',
    name: '消息队列',
    code: 'MQ-001',
    ci_type: 'middleware',
    status: 'online',
    description: 'RabbitMQ 消息队列',
    environment: 'production',
    owner: 'admin',
    createdAt: '2024-01-05T10:00:00Z',
    updatedAt: '2024-01-05T10:00:00Z',
  },
]

export const handlers = [
  http.post('http://localhost:3000/api/auth/login', async ({ request }) => {
    await delay(300)
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

  http.get('http://localhost:3000/api/auth/me', async ({ request }) => {
    await delay(200)
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json({
        success: false,
        error: { code: 'UNAUTHORIZED', message: '未授权' }
      }, { status: 401 })
    }
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

  http.get('http://localhost:3000/api/cis', async ({ request }) => {
    await delay(300)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const page_size = parseInt(url.searchParams.get('page_size') || '10')
    const name = url.searchParams.get('name') || ''
    const type = url.searchParams.get('ci_type') || ''
    const status = url.searchParams.get('status') || ''

    let filteredCIs = [...mockCIs].filter(ci => {
      if (name && !ci.name.toLowerCase().includes(name.toLowerCase())) return false
      if (type && ci.ci_type !== type) return false
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
        total_pages: Math.ceil(total / page_size),
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
    const body = await request.json()
    
    console.log('Received POST request body:', JSON.stringify(body, null, 2))
    console.log('Existing CIs:', JSON.stringify(mockCIs.map(ci => ({id: ci.id, code: ci.code})), null, 2))
    
    // 检查代码唯一性
    const existingCI = mockCIs.find(ci => ci.code === body.code)
    if (existingCI) {
      console.log('Duplicate code found:', body.code)
      return HttpResponse.json({
        success: false,
        error: {
          code: 'DUPLICATE_CODE',
          message: '配置项代码已存在',
        },
      }, { status: 400 })
    }

    // 确保新创建的CI包含ci_type字段
    const newCI = {
      id: String(mockCIs.length + 1),
      ...body,
      ci_type: body.ci_type || 'server', // 默认类型
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    mockCIs.push(newCI)
    console.log('Created new CI:', JSON.stringify(newCI, null, 2))

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

  http.get<{ path: string }>('http://localhost:3000/*path', () => {
    return passthrough()
  }),
  http.post<{ path: string }>('http://localhost:3000/*path', () => {
    return passthrough()
  }),
]
