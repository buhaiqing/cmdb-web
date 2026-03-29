/**
 * 测试数据工厂 - 生成测试数据
 */

export interface UserData {
  username: string
  password: string
  email: string
  full_name?: string
}

export interface CIData {
  code: string
  name: string
  ci_type: string
  status: string
  environment: string
  description?: string
  owner?: string
}

export interface ChangeData {
  ci_id: number
  change_type: 'create' | 'update' | 'delete'
  change_reason: string
}

export interface RoleData {
  name: string
  code: string
  description?: string
  permission_ids?: number[]
}

export interface AuditLogData {
  user_id?: number
  username?: string
  action: 'create' | 'update' | 'delete' | 'login' | 'logout' | 'view'
  resource_type: string
  resource_id?: number
}

/**
 * 用户数据工厂
 */
export class UserFactory {
  static admin(): UserData {
    return {
      username: 'admin',
      password: 'admin123',
      email: 'admin@example.com',
      full_name: '管理员',
    }
  }

  static user(): UserData {
    return {
      username: 'user',
      password: 'user123',
      email: 'user@example.com',
      full_name: '普通用户',
    }
  }

  static readonlyUser(): UserData {
    return {
      username: 'readonly',
      password: 'readonly123',
      email: 'readonly@example.com',
      full_name: '只读用户',
    }
  }

  static auditor(): UserData {
    return {
      username: 'auditor',
      password: 'auditor123',
      email: 'auditor@example.com',
      full_name: '审计员',
    }
  }

  static random(prefix: string = 'test'): UserData {
    const timestamp = Date.now()
    return {
      username: `${prefix}_${timestamp}`,
      password: 'password123',
      email: `${prefix}_${timestamp}@example.com`,
      full_name: `测试用户 ${timestamp}`,
    }
  }

  static invalid(): UserData {
    return {
      username: 'invalid',
      password: 'wrongpassword',
      email: 'invalid@example.com',
    }
  }
}

/**
 * 配置项数据工厂
 */
export class CIFactory {
  static server(overrides?: Partial<CIData>): CIData {
    return {
      code: `SRV-${Date.now()}`,
      name: `测试服务器 ${Date.now()}`,
      ci_type: '服务器',
      status: '在线',
      environment: '生产',
      description: '测试服务器',
      ...overrides,
    }
  }

  static database(overrides?: Partial<CIData>): CIData {
    return {
      code: `DB-${Date.now()}`,
      name: `测试数据库 ${Date.now()}`,
      ci_type: '数据库',
      status: '在线',
      environment: '生产',
      description: '测试数据库',
      ...overrides,
    }
  }

  static application(overrides?: Partial<CIData>): CIData {
    return {
      code: `APP-${Date.now()}`,
      name: `测试应用 ${Date.now()}`,
      ci_type: '应用',
      status: '在线',
      environment: '生产',
      description: '测试应用',
      ...overrides,
    }
  }

  static networkDevice(overrides?: Partial<CIData>): CIData {
    return {
      code: `NET-${Date.now()}`,
      name: `测试网络设备 ${Date.now()}`,
      ci_type: '网络设备',
      status: '在线',
      environment: '生产',
      description: '测试网络设备',
      ...overrides,
    }
  }

  static random(ci_type: string = '服务器'): CIData {
    const timestamp = Date.now()
    return {
      code: `TEST-${timestamp}`,
      name: `测试${ci_type} ${timestamp}`,
      ci_type,
      status: '在线',
      environment: '生产',
      description: `测试${ci_type}`,
    }
  }

  static invalid(): CIData {
    return {
      code: '',
      name: '',
      ci_type: '服务器',
      status: '在线',
      environment: '生产',
    }
  }
}

/**
 * 变更数据工厂
 */
export class ChangeFactory {
  static create(ciId: number): ChangeData {
    return {
      ci_id: ciId,
      change_type: 'create',
      change_reason: `创建配置项 - ${Date.now()}`,
    }
  }

  static update(ciId: number): ChangeData {
    return {
      ci_id: ciId,
      change_type: 'update',
      change_reason: `更新配置项 - ${Date.now()}`,
    }
  }

  static delete(ciId: number): ChangeData {
    return {
      ci_id: ciId,
      change_type: 'delete',
      change_reason: `删除配置项 - ${Date.now()}`,
    }
  }

  static random(ciId: number): ChangeData {
    const types: Array<'create' | 'update' | 'delete'> = ['create', 'update', 'delete']
    return {
      ci_id: ciId,
      change_type: types[Math.floor(Math.random() * types.length)],
      change_reason: `测试变更 - ${Date.now()}`,
    }
  }
}

/**
 * 角色数据工厂
 */
export class RoleFactory {
  static admin(): RoleData {
    return {
      name: '系统管理员',
      code: 'admin',
      description: '拥有系统全部权限',
      permission_ids: [1, 2, 3, 4, 5],
    }
  }

  static operator(): RoleData {
    return {
      name: '运维工程师',
      code: 'operator',
      description: '配置项管理权限',
      permission_ids: [1, 2, 3],
    }
  }

  static readonly(): RoleData {
    return {
      name: '只读用户',
      code: 'readonly',
      description: '只读权限',
      permission_ids: [1],
    }
  }

  static auditor(): RoleData {
    return {
      name: '审计员',
      code: 'auditor',
      description: '审计日志查看权限',
      permission_ids: [1, 6],
    }
  }

  static random(): RoleData {
    const timestamp = Date.now()
    return {
      name: `测试角色 ${timestamp}`,
      code: `test_role_${timestamp}`,
      description: '测试角色描述',
    }
  }
}

/**
 * 审计日志数据工厂
 */
export class AuditLogFactory {
  static login(username: string): AuditLogData {
    return {
      username,
      action: 'login',
      resource_type: 'user',
    }
  }

  static logout(username: string): AuditLogData {
    return {
      username,
      action: 'logout',
      resource_type: 'user',
    }
  }

  static createCI(userId: number, ciId: number): AuditLogData {
    return {
      user_id: userId,
      action: 'create',
      resource_type: 'ci',
      resource_id: ciId,
    }
  }

  static updateCI(userId: number, ciId: number): AuditLogData {
    return {
      user_id: userId,
      action: 'update',
      resource_type: 'ci',
      resource_id: ciId,
    }
  }

  static deleteCI(userId: number, ciId: number): AuditLogData {
    return {
      user_id: userId,
      action: 'delete',
      resource_type: 'ci',
      resource_id: ciId,
    }
  }
}
