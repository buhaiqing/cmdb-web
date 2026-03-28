import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 响应数据类型
export interface ApiResponse<T = unknown> {
  success: boolean
  message: string
  data?: T
  error?: {
    code: string
    message: string
    details?: string[]
  }
}

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data

    if (!res.success && res.error) {
      ElMessage.error(res.error.message || '请求失败')

      if (res.error.code === 'UNAUTHORIZED' || res.error.code === 'INVALID_CREDENTIALS') {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }

      return Promise.reject(new Error(res.error.message || '请求失败'))
    }

    return res
  },
  (error) => {
    console.error('HTTP 错误:', error)

    if (error.response) {
      const status = error.response.status
      const data = error.response.data as ApiResponse
      
      if (data && data.error && data.error.message) {
        ElMessage.error(data.error.message)
      } else {
        switch (status) {
          case 401:
            ElMessage.error('未授权，请重新登录')
            localStorage.removeItem('token')
            window.location.href = '/login'
            break
          case 403:
            ElMessage.error('权限不足')
            break
          case 404:
            ElMessage.error('请求的资源不存在')
            break
          case 500:
            ElMessage.error('服务器内部错误')
            break
          default:
            ElMessage.error(error.message || '请求失败')
        }
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error(error.message || '请求失败')
    }

    return Promise.reject(error)
  }
)

// 导出请求方法
export const http = {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.get(url, config)
  },

  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.post(url, data, config)
  },

  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.put(url, data, config)
  },

  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.delete(url, config)
  },
}
