import { http } from './request'
import type { ApiResponse } from './request'

// 配置项类型
export type CIType =
  | 'server'
  | 'network_device'
  | 'database'
  | 'middleware'
  | 'application'
  | 'container'
  | 'k8s_resource'
  | 'cloud_resource'

// 配置项状态
export type CIStatus = 'online' | 'offline' | 'maintenance' | 'decommissioned'

// 配置项
export interface CI {
  id: number
  ci_type: CIType
  name: string
  code: string
  description?: string
  status: CIStatus
  environment: string
  owner?: string
  tags?: Record<string, unknown>
  created_at: string
  updated_at: string
}

// 配置项列表响应
export interface CIListResponse {
  items: CI[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 创建配置项请求
export interface CICreateParams {
  ci_type: CIType
  name: string
  code: string
  description?: string
  status?: CIStatus
  environment: string
  owner?: string
  tags?: Record<string, unknown>
}

// 更新配置项请求
export interface CIUpdateParams {
  name?: string
  description?: string
  status?: CIStatus
  environment?: string
  owner?: string
  tags?: Record<string, unknown>
}

// 搜索配置项请求
export interface CISearchParams {
  ci_type?: CIType
  name?: string
  code?: string
  status?: CIStatus
  environment?: string
  owner?: string
  page?: number
  page_size?: number
}

/**
 * 获取配置项列表
 */
export function getCIList(params: {
  name?: string
  ci_type?: CIType
  status?: CIStatus
  environment?: string
  page: number
  page_size: number
}): Promise<ApiResponse<CIListResponse>> {
  return http.get<CIListResponse>('/cis', { params })
}

/**
 * 搜索配置项
 */
export function searchCIs(params: CISearchParams): Promise<ApiResponse<CIListResponse>> {
  return http.post<CIListResponse>('/cis/search', params)
}

/**
 * 获取配置项详情
 */
export function getCIDetail(id: number): Promise<ApiResponse<CI>> {
  return http.get<CI>(`/cis/${id}`)
}

/**
 * 创建配置项
 */
export function createCI(data: CICreateParams): Promise<ApiResponse<CI>> {
  return http.post<CI>('/cis', data)
}

/**
 * 更新配置项
 */
export function updateCI(id: number, data: CIUpdateParams): Promise<ApiResponse<CI>> {
  return http.put<CI>(`/cis/${id}`, data)
}

/**
 * 删除配置项
 */
export function deleteCI(id: number): Promise<ApiResponse<void>> {
  return http.delete<void>(`/cis/${id}`)
}

/**
 * 获取配置项关系
 */
export function getCIRelations(id: number): Promise<ApiResponse<unknown[]>> {
  return http.get(`/cis/${id}/relations`)
}

/**
 * 创建配置项关系
 */
export function createCIRelation(
  ciId: number,
  data: { target_ci_id: number; relation_type: string; description?: string }
): Promise<ApiResponse<unknown>> {
  return http.post(`/cis/${ciId}/relations`, data)
}

/**
 * 删除配置项关系
 */
export function deleteCIRelation(relationId: number): Promise<ApiResponse<void>> {
  return http.delete<void>(`/cis/relations/${relationId}`)
}
