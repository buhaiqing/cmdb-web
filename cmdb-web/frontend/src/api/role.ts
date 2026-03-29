import { http } from './request'
import type { ApiResponse } from './request'

export interface Permission {
  id: number
  code: string
  name: string
  description?: string
  module: string
}

export interface Role {
  id: number
  name: string
  code: string
  description?: string
  permissions: Permission[]
  user_count: number
  created_at: string
  updated_at: string
}

export interface RoleListResponse {
  items: Role[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface RoleCreateParams {
  name: string
  code: string
  description?: string
  permission_ids: number[]
}

export interface RoleUpdateParams {
  name?: string
  description?: string
  permission_ids?: number[]
}

export interface RoleSearchParams {
  name?: string
  code?: string
  page?: number
  page_size?: number
}

export function getRoleList(params: {
  page: number
  page_size: number
  name?: string
}): Promise<ApiResponse<RoleListResponse>> {
  return http.get<RoleListResponse>('/roles', { params })
}

export function getRoleDetail(id: number): Promise<ApiResponse<Role>> {
  return http.get<Role>(`/roles/${id}`)
}

export function createRole(data: RoleCreateParams): Promise<ApiResponse<Role>> {
  return http.post<Role>('/roles', data)
}

export function updateRole(id: number, data: RoleUpdateParams): Promise<ApiResponse<Role>> {
  return http.put<Role>(`/roles/${id}`, data)
}

export function deleteRole(id: number): Promise<ApiResponse<void>> {
  return http.delete<void>(`/roles/${id}`)
}

export function getPermissionList(): Promise<ApiResponse<Permission[]>> {
  return http.get<Permission[]>('/permissions')
}

export function assignRoleToUser(userId: number, roleId: number): Promise<ApiResponse<void>> {
  return http.post<void>(`/users/${userId}/roles`, { role_id: roleId })
}

export function removeRoleFromUser(userId: number, roleId: number): Promise<ApiResponse<void>> {
  return http.delete<void>(`/users/${userId}/roles/${roleId}`)
}
