import { http } from './request'
import type { ApiResponse } from './request'

export type AuditAction = 'create' | 'update' | 'delete' | 'login' | 'logout' | 'view'

export interface AuditLog {
  id: number
  user_id: number
  username: string
  action: AuditAction
  resource_type: string
  resource_id?: number
  resource_name?: string
  detail?: Record<string, unknown>
  ip_address: string
  user_agent?: string
  created_at: string
}

export interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AuditLogSearchParams {
  user_id?: number
  username?: string
  action?: AuditAction
  resource_type?: string
  resource_id?: number
  start_date?: string
  end_date?: string
  ip_address?: string
  page?: number
  page_size?: number
}

export function getAuditLogList(params: {
  page: number
  page_size: number
  user_id?: number
  username?: string
  action?: AuditAction
  resource_type?: string
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<AuditLogListResponse>> {
  return http.get<AuditLogListResponse>('/audit-logs', { params })
}

export function getAuditLogDetail(id: number): Promise<ApiResponse<AuditLog>> {
  return http.get<AuditLog>(`/audit-logs/${id}`)
}

export function searchAuditLogs(params: AuditLogSearchParams): Promise<ApiResponse<AuditLogListResponse>> {
  return http.post<AuditLogListResponse>('/audit-logs/search', params)
}

export function exportAuditLogs(params: AuditLogSearchParams): Promise<ApiResponse<string>> {
  return http.post<string>('/audit-logs/export', params)
}
