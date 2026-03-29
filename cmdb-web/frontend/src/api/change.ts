import { http } from './request'
import type { ApiResponse } from './request'

export type ChangeStatus = 'pending' | 'approved' | 'rejected' | 'completed'
export type ChangeType = 'create' | 'update' | 'delete'

export interface Change {
  id: number
  ci_id: number
  ci_name: string
  change_type: ChangeType
  change_reason: string
  status: ChangeStatus
  old_value?: Record<string, unknown>
  new_value?: Record<string, unknown>
  created_by: {
    id: number
    username: string
  }
  approved_by?: {
    id: number
    username: string
  }
  approved_at?: string
  created_at: string
  updated_at: string
}

export interface ChangeListResponse {
  items: Change[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ChangeCreateParams {
  ci_id: number
  change_type: ChangeType
  change_reason: string
  old_value?: Record<string, unknown>
  new_value?: Record<string, unknown>
}

export interface ChangeSearchParams {
  ci_id?: number
  change_type?: ChangeType
  status?: ChangeStatus
  created_by?: number
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

export function getChangeList(params: {
  page: number
  page_size: number
  ci_id?: number
  status?: ChangeStatus
  change_type?: ChangeType
}): Promise<ApiResponse<ChangeListResponse>> {
  return http.get<ChangeListResponse>('/changes', { params })
}

export function getChangeDetail(id: number): Promise<ApiResponse<Change>> {
  return http.get<Change>(`/changes/${id}`)
}

export function createChange(data: ChangeCreateParams): Promise<ApiResponse<Change>> {
  return http.post<Change>('/changes', data)
}

export function approveChange(id: number): Promise<ApiResponse<Change>> {
  return http.post<Change>(`/changes/${id}/approve`)
}

export function rejectChange(id: number, reason: string): Promise<ApiResponse<Change>> {
  return http.post<Change>(`/changes/${id}/reject`, { reason })
}

export function searchChanges(params: ChangeSearchParams): Promise<ApiResponse<ChangeListResponse>> {
  return http.post<ChangeListResponse>('/changes/search', params)
}
