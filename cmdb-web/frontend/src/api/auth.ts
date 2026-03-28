import { http } from './request'
import type { ApiResponse } from './request'

// 登录请求参数
export interface LoginParams {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  email: string
  full_name?: string
  status: 'active' | 'inactive' | 'locked'
  is_superuser: boolean
  created_at: string
  updated_at: string
}

/**
 * 用户登录
 */
export function login(data: LoginParams): Promise<ApiResponse<LoginResponse>> {
  const formData = new URLSearchParams()
  formData.append('username', data.username)
  formData.append('password', data.password)

  return http.post<LoginResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

/**
 * 用户注册
 */
export function register(data: {
  username: string
  email: string
  password: string
  full_name?: string
}): Promise<ApiResponse<UserInfo>> {
  return http.post<UserInfo>('/auth/register', data)
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<ApiResponse<UserInfo>> {
  return http.get<UserInfo>('/auth/me')
}

/**
 * 获取用户列表
 */
export function getUserList(params: {
  page: number
  page_size: number
}): Promise<ApiResponse<{ items: UserInfo[]; total: number; page: number; page_size: number }>> {
  return http.get('/users', { params })
}
