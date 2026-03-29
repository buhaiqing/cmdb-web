import { Page } from '@playwright/test'
import { mockUsers, mockCIs, mockChanges, mockAuditLogs, getDashboardStats, getDashboardData } from '../../../mock/data'

export async function setupApiMocks(page: Page) {
  await page.route('**/api/auth/login', async (route) => {
    const request = route.request()
    const postData = request.postData()
    
    let username = ''
    let password = ''
    if (postData) {
      const params = new URLSearchParams(postData)
      username = params.get('username') || ''
      password = params.get('password') || ''
    }

    const user = mockUsers.find(u => u.username === username && u.password === password)

    if (user) {
      await route.fulfill({
        status: 200,
        json: { success: true, message: '登录成功', data: { access_token: 'mock-jwt-token-' + user.id, token_type: 'Bearer', expires_in: 3600 } },
      })
    } else {
      await route.fulfill({
        status: 401,
        json: { success: false, error: { code: 'INVALID_CREDENTIALS', message: '用户名或密码错误' } },
      })
    }
  })

  await page.route('**/api/auth/logout', async (route) => {
    await route.fulfill({ status: 200, json: { success: true, message: '登出成功' } })
  })

  await page.route('**/api/auth/me', async (route) => {
    const request = route.request()
    const authHeader = request.headers().authorization

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      await route.fulfill({ status: 401, json: { success: false, error: { code: 'UNAUTHORIZED', message: '未授权' } } })
    } else {
      await route.fulfill({
        status: 200,
        json: { success: true, message: '获取用户信息成功', data: { id: 1, username: 'admin', email: 'admin@example.com', full_name: '管理员', status: 'active' as const, is_superuser: true, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' } },
      })
    }
  })

  await page.route('**/api/dashboard', async (route) => {
    await route.fulfill({ status: 200, json: { success: true, data: getDashboardData() } })
  })

  await page.route('**/api/dashboard/stats', async (route) => {
    await route.fulfill({ status: 200, json: { success: true, message: '获取仪表盘统计成功', data: getDashboardStats() } })
  })

  await page.route('**/api/dashboard/chart-data', async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        success: true,
        message: '获取图表数据成功',
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
      },
    })
  })

  await page.route('**/api/cis**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    
    if (url.pathname.match(/\/api\/cis\/[^/]+$/)) {
      const pathParts = url.pathname.split('/')
      const id = pathParts[pathParts.length - 1]
      const ci = mockCIs.find(c => c.id === id)
      
      if (request.method() === 'GET') {
        if (ci) {
          await route.fulfill({ status: 200, json: { success: true, message: '获取配置项成功', data: ci } })
        } else {
          await route.fulfill({ status: 404, json: { success: false, error: { code: 'NOT_FOUND', message: '配置项不存在' } } })
        }
      } else if (request.method() === 'PUT') {
        const index = mockCIs.findIndex(c => c.id === id)
        if (index !== -1) {
          const body = request.postDataJSON()
          mockCIs[index] = { ...mockCIs[index], ...body, updated_at: new Date().toISOString() }
          await route.fulfill({ status: 200, json: { success: true, message: '更新成功', data: mockCIs[index] } })
        } else {
          await route.fulfill({ status: 404, json: { success: false, error: { code: 'NOT_FOUND', message: '配置项不存在' } } })
        }
      } else if (request.method() === 'DELETE') {
        const index = mockCIs.findIndex(c => c.id === id)
        if (index !== -1) {
          mockCIs.splice(index, 1)
          await route.fulfill({ status: 200, json: { success: true, message: '删除成功' } })
        } else {
          await route.fulfill({ status: 404, json: { success: false, error: { code: 'NOT_FOUND', message: '配置项不存在' } } })
        }
      }
      return
    }
    
    const pageParam = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '10')
    const name = url.searchParams.get('name') || ''
    const ci_type = url.searchParams.get('ci_type') || ''
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
    const start = (pageParam - 1) * pageSize
    const items = filteredCIs.slice(start, start + pageSize)

    await route.fulfill({
      status: 200,
      json: { success: true, message: '获取配置项列表成功', data: { items, total, page: pageParam, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } },
    })
  })

  await page.route('**/api/cis', async (route) => {
    const request = route.request()
    if (request.method() === 'POST') {
      const body = request.postDataJSON()
      const existingCI = mockCIs.find(ci => ci.code === body.code)
      if (existingCI) {
        await route.fulfill({ status: 400, json: { success: false, error: { code: 'DUPLICATE_CODE', message: '配置项代码已存在' } } })
      } else {
        const newCI = {
          id: String(mockCIs.length + 1),
          ...body,
          ci_type: body.ci_type || 'server',
          status: body.status || 'offline',
          environment: body.environment || 'development',
          owner: body.owner || 'admin',
          description: body.description || '',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        mockCIs.push(newCI)
        await route.fulfill({ status: 201, json: { success: true, message: '创建成功', data: newCI } })
      }
    }
  })

  await page.route('**/api/changes**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    
    if (url.pathname.match(/\/api\/changes\/[^/]+$/)) {
      const pathParts = url.pathname.split('/')
      const id = pathParts[pathParts.length - 1]
      const change = mockChanges.find(c => c.id === id)
      
      if (request.method() === 'GET') {
        if (change) {
          await route.fulfill({ status: 200, json: { success: true, message: '获取变更详情成功', data: change } })
        } else {
          await route.fulfill({ status: 404, json: { success: false, error: { code: 'NOT_FOUND', message: '变更不存在' } } })
        }
      } else if (request.method() === 'PUT') {
        const index = mockChanges.findIndex(c => c.id === id)
        if (index !== -1) {
          const body = request.postDataJSON()
          mockChanges[index] = { ...mockChanges[index], ...body, updated_at: new Date().toISOString() }
          await route.fulfill({ status: 200, json: { success: true, message: '更新成功', data: mockChanges[index] } })
        } else {
          await route.fulfill({ status: 404, json: { success: false, error: { code: 'NOT_FOUND', message: '变更不存在' } } })
        }
      }
      return
    }
    
    const pageParam = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '10')
    const status = url.searchParams.get('status') || ''
    const changeType = url.searchParams.get('change_type') || ''

    let filteredChanges = mockChanges.filter(change => {
      if (status && change.status !== status) return false
      if (changeType && change.change_type !== changeType) return false
      return true
    })

    const total = filteredChanges.length
    const start = (pageParam - 1) * pageSize
    const items = filteredChanges.slice(start, start + pageSize)

    await route.fulfill({
      status: 200,
      json: { success: true, message: '获取变更列表成功', data: { items, total, page: pageParam, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } },
    })
  })

  await page.route('**/api/changes', async (route) => {
    const request = route.request()
    if (request.method() === 'POST') {
      const body = request.postDataJSON()
      const newChange = {
        id: String(mockChanges.length + 1),
        title: body.title,
        description: body.description,
        status: 'pending',
        change_type: body.change_type || 'normal',
        priority: body.priority || 'medium',
        ci_id: body.ci_id,
        ci_name: body.ci_name,
        ci_code: body.ci_code,
        requester: 'admin',
        approver: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        planned_start: body.planned_start,
        planned_end: body.planned_end,
      }
      mockChanges.push(newChange)
      await route.fulfill({ status: 201, json: { success: true, message: '创建成功', data: newChange } })
    }
  })

  await page.route('**/api/audit-logs**', async (route) => {
    const request = route.request()
    const url = new URL(request.url)
    const pageParam = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '10')
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
    const start = (pageParam - 1) * pageSize
    const items = filteredLogs.slice(start, start + pageSize)
    
    await route.fulfill({
      status: 200,
      json: { success: true, message: '获取审计日志列表成功', data: { items, total, page: pageParam, page_size: pageSize, total_pages: Math.ceil(total / pageSize) } },
    })
  })

  await page.route('**/api/users**', async (route) => {
    await route.fulfill({
      status: 200,
      json: {
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
      },
    })
  })
}

export function resetMockData() {
  console.log('Mock data reset')
}