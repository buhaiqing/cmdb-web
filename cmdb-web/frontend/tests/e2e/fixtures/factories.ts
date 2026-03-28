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

/**
 * 用户数据工厂
 */
export class UserFactory {
  /**
   * 生成管理员用户
   */
  static admin(): UserData {
    return {
      username: 'admin',
      password: 'admin123',
      email: 'admin@example.com',
      full_name: '管理员',
    }
  }

  /**
   * 生成普通用户
   */
  static user(): UserData {
    return {
      username: 'user',
      password: 'user123',
      email: 'user@example.com',
      full_name: '普通用户',
    }
  }

  /**
   * 生成随机用户
   */
  static random(prefix: string = 'test'): UserData {
    const timestamp = Date.now()
    return {
      username: `${prefix}_${timestamp}`,
      password: 'password123',
      email: `${prefix}_${timestamp}@example.com`,
      full_name: `测试用户 ${timestamp}`,
    }
  }

  /**
   * 生成无效用户数据
   */
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
  /**
   * 生成服务器类型配置项
   */
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

  /**
   * 生成数据库类型配置项
   */
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

  /**
   * 生成应用类型配置项
   */
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

  /**
   * 生成随机配置项
   */
  static random(ci_type: string = '服务器'): CIData {
    const timestamp = Date.now()
    return {
      code: `${ci_type}${timestamp}`,
      name: `测试${ci_type} ${timestamp}`,
      ci_type,
      status: '在线',
      environment: '生产',
      description: `测试${ci_type}`,
    }
  }

  /**
   * 生成无效配置项数据
   */
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
