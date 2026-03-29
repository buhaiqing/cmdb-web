import { http, HttpResponse, delay } from 'msw'
import { mockUsers, mockCIs, mockChanges, mockAuditLogs, getDashboardStats, getDashboardData } from './data'

export const handlers = [
  http.post('/api/auth/login', async ({ request }) => {
    await delay(300)
    const formData = await request.formData()
    const username = formData.get('username') as string
    const password = formData.get('password') as string
    const user = mockUsers.find(u => u.username === username && u.password === password)
    if (user) {
      return HttpResponse.json({ success: true, message: '登录成功', data: { access_token: 'mock-jwt-token-' + user.id, token_type: 'Bearer', expires_in: 3600 } })
    }
    return HttpResponse.json({ success: false, message: '用户名或密码错误', error: { code: 'INVALID_CREDENTIALS', message: '用户名或密码错误' } }, { status: 401 })
  }),

  http.post('/api/auth/logout', async () => {
    await delay(200)
    return HttpResponse.json({ success: true, message: '登出成功' })
  }),

  http.get('/api/auth/me', async ({ request }) => {
    await delay(200)
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json({ success: false, error: { code: 'UNAUTHORIZED', message: '未授权' } }, { status: 401 })
    }
    return HttpResponse.json({ success: true, message: '获取用户信息成功', data: { id: 1, username: 'admin', email: 'admin@example.com', full_name: '管理员', status: 'active', is_superuser: true, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' } })
  }),

  http.get('/api/dashboard', async () => {
    await delay(200)
    return HttpResponse.json({ success: true, data: getDashboardData() })
  }),

  http.get('/api/dashboard/stats', async () => {
    await delay(200)
    return HttpResponse.json({ success: true, data: getDashboardStats() })
  }),

  http.get('/api/dashboard/chart-data', async () => {
    await delay(200)
    return HttpResponse.json({
      success: true,
      data: {
        cis_by_type: [
          { type: 'server', count: 8, label: '服务器' },
          { type: 'database', count: 6, label: '数据库' },
          { type: 'application', count: 7, label: '应用' },
          { type: 'middleware', count: 4, label: '中间件' },
          { type: 'network_device', count: 3, label: '网络设备' },
          { type: 'container', count: 2, label: '容器' },
        ],
        cis_by_environment: [
          { environment: 'production', count: 18, label: '生产环境' },
          { environment: 'testing', count: 6, label: '测试环境' },
          { environment: 'development', count: 2, label: '开发环境' },
        ],
        changes_trend: [
          { date: '2024-02-01', total: 12, completed: 10 },
          { date: '2024-02-08', total: 8, completed: 7 },
          { date: '2024-02-15', total: 15, completed: 12 },
          { date: '2024-02-22', total: 10, completed: 8 },
          { date: '2024-03-01', total: 18, completed: 14 },
          { date: '2024-03-08', total: 5, completed: 3 },
        ],
      },
    })
  }),

  http.get('/api/cis', async ({ request }) => {
    await delay(300)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || url.searchParams.get('page_size') || '10')
    const name = url.searchParams.get('name') || ''
    const ci_type = url.searchParams.get('ci_type') || url.searchParams.get('type') || ''
    const status = url.searchParams.get('status') || ''
    const environment = url.searchParams.get('environment') || ''
    
    let filteredCIs = mockCIs.filter(ci => {
      if (name && !ci.name.toLowerCase().includes(name.toLowerCase()) && !ci.code.toLowerCase().includes(name.toLowerCase())) return false
      if (ci_type && ci.ci_type !== ci_type) return false
      if (status && ci.status !== status) return false
      if (environment && ci.environment !== environment) return false
      return true
    })
    
    const total = filteredCIs.length
    const start = (page - 1) * pageSize
    const items = filteredCIs.slice(start, start + pageSize)
    
    return HttpResponse.json({ success: true, data: { items, total, page, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } })
  }),

  http.get('/api/cis/:id', async ({ params }) => {
    await delay(200)
    const ci = mockCIs.find(c => c.id === params.id)
    if (ci) return HttpResponse.json({ success: true, data: ci })
    return HttpResponse.json({ success: false, message: '配置项不存在' }, { status: 404 })
  }),

  http.post('/api/cis', async ({ request }) => {
    await delay(300)
    const body = await request.json() as Record<string, unknown>
    const newCI = {
      id: String(mockCIs.length + 1),
      name: body.name as string,
      code: body.code as string,
      ci_type: body.ci_type || body.type as string,
      status: body.status as string || 'offline',
      environment: body.environment as string || 'development',
      owner: body.owner as string || 'admin',
      description: (body.description as string) || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    mockCIs.push(newCI)
    return HttpResponse.json({ success: true, data: newCI, message: '创建成功' }, { status: 201 })
  }),

  http.put('/api/cis/:id', async ({ params, request }) => {
    await delay(300)
    const index = mockCIs.findIndex(c => c.id === params.id)
    if (index !== -1) {
      const body = await request.json() as Record<string, unknown>
      mockCIs[index] = { ...mockCIs[index], ...body, updated_at: new Date().toISOString() }
      return HttpResponse.json({ success: true, data: mockCIs[index], message: '更新成功' })
    }
    return HttpResponse.json({ success: false, message: '配置项不存在' }, { status: 404 })
  }),

  http.delete('/api/cis/:id', async ({ params }) => {
    await delay(300)
    const index = mockCIs.findIndex(c => c.id === params.id)
    if (index !== -1) {
      mockCIs.splice(index, 1)
      return HttpResponse.json({ success: true, message: '删除成功' })
    }
    return HttpResponse.json({ success: false, message: '配置项不存在' }, { status: 404 })
  }),

  http.get('/api/changes', async ({ request }) => {
    await delay(300)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || url.searchParams.get('page_size') || '10')
    const status = url.searchParams.get('status') || ''
    const change_type = url.searchParams.get('change_type') || ''
    
    let filteredChanges = mockChanges.filter(change => {
      if (status && change.status !== status) return false
      if (change_type && change.change_type !== change_type) return false
      return true
    })
    
    const total = filteredChanges.length
    const start = (page - 1) * pageSize
    const items = filteredChanges.slice(start, start + pageSize)
    
    return HttpResponse.json({ success: true, data: { items, total, page, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } })
  }),

  http.get('/api/changes/:id', async ({ params }) => {
    await delay(200)
    const change = mockChanges.find(c => c.id === params.id)
    if (change) return HttpResponse.json({ success: true, data: change })
    return HttpResponse.json({ success: false, message: '变更不存在' }, { status: 404 })
  }),

  http.post('/api/changes', async ({ request }) => {
    await delay(300)
    const body = await request.json() as Record<string, unknown>
    const newChange = {
      id: String(mockChanges.length + 1),
      title: body.title as string,
      description: body.description as string,
      status: 'pending',
      change_type: body.change_type as string || 'normal',
      priority: body.priority as string || 'medium',
      ci_id: body.ci_id as string,
      ci_name: body.ci_name as string,
      ci_code: body.ci_code as string,
      requester: 'admin',
      approver: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      planned_start: body.planned_start as string,
      planned_end: body.planned_end as string,
    }
    mockChanges.push(newChange)
    return HttpResponse.json({ success: true, data: newChange, message: '创建成功' }, { status: 201 })
  }),

  http.put('/api/changes/:id', async ({ params, request }) => {
    await delay(300)
    const index = mockChanges.findIndex(c => c.id === params.id)
    if (index !== -1) {
      const body = await request.json() as Record<string, unknown>
      mockChanges[index] = { ...mockChanges[index], ...body, updated_at: new Date().toISOString() }
      return HttpResponse.json({ success: true, data: mockChanges[index], message: '更新成功' })
    }
    return HttpResponse.json({ success: false, message: '变更不存在' }, { status: 404 })
  }),

  http.get('/api/audit-logs', async ({ request }) => {
    await delay(300)
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('pageSize') || url.searchParams.get('page_size') || '10')
    const action = url.searchParams.get('action') || ''
    const resource_type = url.searchParams.get('resource_type') || ''
    const user = url.searchParams.get('user') || ''
    
    let filteredLogs = mockAuditLogs.filter(log => {
      if (action && log.action !== action) return false
      if (resource_type && log.resource_type !== resource_type) return false
      if (user && log.user !== user) return false
      return true
    })
    
    const total = filteredLogs.length
    const start = (page - 1) * pageSize
    const items = filteredLogs.slice(start, start + pageSize)
    
    return HttpResponse.json({ success: true, data: { items, total, page, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } })
  }),

  http.get('/api/users', async () => {
    await delay(200)
    return HttpResponse.json({
      success: true,
      data: {
        items: mockUsers.map(({ password, ...user }) => ({ ...user, id: parseInt(user.id), created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' })),
        total: mockUsers.length,
        page: 1,
        page_size: 10,
      },
    })
  }),
]