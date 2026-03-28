/**
 * 日期格式化
 * @param date 日期对象或日期字符串
 * @param format 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期字符串
 */
export function formatDate(
  date: string | number | Date | null | undefined,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 相对时间格式化
 * @param date 日期对象或时间戳
 * @returns 相对时间字符串（如：5 分钟前）
 */
export function formatRelativeTime(
  date: string | number | Date | null | undefined
): string {
  if (!date) return ''

  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)

  if (years > 0) return `${years}年前`
  if (months > 0) return `${months}个月前`
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  if (seconds > 0) return `${seconds}秒前`
  return '刚刚'
}

/**
 * 货币格式化
 * @param amount 金额
 * @param currency 货币符号
 * @param decimals 小数位数
 * @returns 格式化后的货币字符串
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = '¥',
  decimals: number = 2
): string {
  if (amount === null || amount === undefined || amount === '') return ''

  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return ''

  const formatted = num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return `${currency}${formatted}`
}

/**
 * 数字格式化（千分位）
 * @param num 数字
 * @param decimals 小数位数
 * @returns 格式化后的数字字符串
 */
export function formatNumber(
  num: number | string | null | undefined,
  decimals: number = 0
): string {
  if (num === null || num === undefined || num === '') return ''

  const n = typeof num === 'string' ? parseFloat(num) : num
  if (isNaN(n)) return ''

  return n.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 状态格式化
 * @param status 状态值
 * @param statusMap 状态映射表
 * @returns 格式化后的状态文本
 */
export function formatStatus(
  status: string | number | null | undefined,
  statusMap?: Record<string, string>
): string {
  if (status === null || status === undefined || status === '') return ''

  const defaultMap: Record<string, string> = {
    active: '活跃',
    inactive: '未激活',
    pending: '待处理',
    running: '运行中',
    stopped: '已停止',
    error: '错误',
    success: '成功',
    failed: '失败'
  }

  const map = statusMap || defaultMap
  return map[String(status)] || String(status)
}

/**
 * 文本截断
 * @param text 文本
 * @param length 最大长度
 * @param suffix 后缀
 * @returns 截断后的文本
 */
export function truncateText(
  text: string | null | undefined,
  length: number = 50,
  suffix: string = '...'
): string {
  if (!text) return ''

  if (text.length <= length) return text

  return text.substring(0, length) + suffix
}

/**
 * 文件大小格式化
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的大小字符串
 */
export function formatFileSize(
  bytes: number | string | null | undefined,
  decimals: number = 2
): string {
  if (bytes === null || bytes === undefined || bytes === '') return ''

  const num = typeof bytes === 'string' ? parseFloat(bytes) : bytes
  if (isNaN(num) || num === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const k = 1024
  const i = Math.floor(Math.log(num) / Math.log(k))

  return `${(num / Math.pow(k, i)).toFixed(decimals)} ${units[i]}`
}

/**
 * 百分比格式化
 * @param value 数值（0-1 之间的小数或百分比数值）
 * @param decimals 小数位数
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(
  value: number | string | null | undefined,
  decimals: number = 1
): string {
  if (value === null || value === undefined || value === '') return ''

  let num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return ''

  // 如果数值小于等于 1，认为是小数，转换为百分比
  if (num <= 1) {
    num = num * 100
  }

  return `${num.toFixed(decimals)}%`
}
