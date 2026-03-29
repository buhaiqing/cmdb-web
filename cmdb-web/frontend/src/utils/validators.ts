/**
 * 邮箱验证
 * @param email 邮箱地址
 * @returns 验证结果
 */
export function validateEmail(email: string): { valid: boolean; message?: string } {
  if (!email || email.trim() === '') {
    return { valid: false, message: '邮箱不能为空' }
  }

  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(email)) {
    return { valid: false, message: '邮箱格式不正确' }
  }

  return { valid: true }
}

/**
 * 手机号验证（中国大陆）
 * @param phone 手机号
 * @returns 验证结果
 */
export function validatePhone(phone: string): { valid: boolean; message?: string } {
  if (!phone || phone.trim() === '') {
    return { valid: false, message: '手机号不能为空' }
  }

  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone)) {
    return { valid: false, message: '手机号格式不正确' }
  }

  return { valid: true }
}

/**
 * 必填验证
 * @param value 值
 * @param fieldName 字段名称
 * @returns 验证结果
 */
export function validateRequired(
  value: any,
  fieldName: string = '字段'
): { valid: boolean; message?: string } {
  if (value === null || value === undefined || value === '') {
    return { valid: false, message: `${fieldName}不能为空` }
  }

  if (Array.isArray(value) && value.length === 0) {
    return { valid: false, message: `${fieldName}不能为空` }
  }

  return { valid: true }
}

/**
 * 长度验证
 * @param value 值
 * @param min 最小长度
 * @param max 最大长度
 * @param fieldName 字段名称
 * @returns 验证结果
 */
export function validateLength(
  value: string,
  min?: number,
  max?: number,
  fieldName: string = '字段'
): { valid: boolean; message?: string } {
  if (!value) {
    return { valid: true } // 空值由 required 规则处理
  }

  const length = value.length

  if (min !== undefined && length < min) {
    return { valid: false, message: `${fieldName}长度不能少于${min}个字符` }
  }

  if (max !== undefined && length > max) {
    return { valid: false, message: `${fieldName}长度不能超过${max}个字符` }
  }

  return { valid: true }
}

/**
 * 密码强度验证
 * @param password 密码
 * @returns 验证结果和强度等级
 */
export function validatePassword(
  password: string
): { valid: boolean; strength: 'weak' | 'medium' | 'strong'; message?: string } {
  if (!password || password.length < 8) {
    return { valid: false, strength: 'weak', message: '密码长度至少为 8 位' }
  }

  const hasLetter = /[a-zA-Z]/.test(password)
  const hasNumber = /\d/.test(password)
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)

  const strengthCount = [hasLetter, hasNumber, hasSpecial].filter(Boolean).length

  let strength: 'weak' | 'medium' | 'strong'
  if (strengthCount <= 1) {
    strength = 'weak'
  } else if (strengthCount === 2) {
    strength = 'medium'
  } else {
    strength = 'strong'
  }

  return { valid: true, strength }
}

/**
 * 数字范围验证
 * @param value 值
 * @param min 最小值
 * @param max 最大值
 * @param fieldName 字段名称
 * @returns 验证结果
 */
export function validateNumberRange(
  value: number | string | null | undefined,
  min?: number,
  max?: number,
  fieldName: string = '字段'
): { valid: boolean; message?: string } {
  if (value === null || value === undefined || value === '') {
    return { valid: true } // 空值由 required 规则处理
  }

  const num = typeof value === 'string' ? parseFloat(value) : value

  if (isNaN(num)) {
    return { valid: false, message: `${fieldName}必须是数字` }
  }

  if (min !== undefined && num < min) {
    return { valid: false, message: `${fieldName}不能小于${min}` }
  }

  if (max !== undefined && num > max) {
    return { valid: false, message: `${fieldName}不能大于${max}` }
  }

  return { valid: true }
}

/**
 * URL 验证
 * @param url URL 地址
 * @returns 验证结果
 */
export function validateUrl(url: string): { valid: boolean; message?: string } {
  if (!url || url.trim() === '') {
    return { valid: false, message: 'URL 不能为空' }
  }

  const urlRegex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/i
  if (!urlRegex.test(url)) {
    return { valid: false, message: 'URL 格式不正确' }
  }

  return { valid: true }
}

/**
 * IP 地址验证
 * @param ip IP 地址
 * @returns 验证结果
 */
export function validateIpAddress(ip: string): { valid: boolean; message?: string } {
  if (!ip || ip.trim() === '') {
    return { valid: false, message: 'IP 地址不能为空' }
  }

  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!ipRegex.test(ip)) {
    return { valid: false, message: 'IP 地址格式不正确' }
  }

  // 验证每段数值是否在 0-255 之间
  const parts = ip.split('.')
  for (const part of parts) {
    const num = parseInt(part, 10)
    if (num < 0 || num > 255) {
      return { valid: false, message: 'IP 地址每段数值必须在 0-255 之间' }
    }
  }

  return { valid: true }
}

/**
 * 组合验证器（用于 Element Plus 表单）
 * @param rules 验证规则数组
 * @returns Element Plus 兼容的验证器函数
 */
export function createValidator(rules: Array<(value: any) => { valid: boolean; message?: string }>) {
  return (_rule: any, value: any, callback: (error?: Error) => void) => {
    for (const validateFn of rules) {
      const result = validateFn(value)
      if (!result.valid) {
        callback(new Error(result.message || '验证失败'))
        return
      }
    }
    callback()
  }
}
