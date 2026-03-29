import { http } from './request'
import type { ApiResponse } from './request'

export interface DashboardStats {
  total_cis: number
  online_cis: number
  offline_cis: number
  maintenance_cis: number
  total_changes: number
  pending_changes: number
  total_users: number
  active_users: number
}

export interface CITypeStats {
  ci_type: string
  count: number
  percentage: number
}

export interface EnvironmentStats {
  environment: string
  count: number
  percentage: number
}

export interface ChangeTrend {
  date: string
  create_count: number
  update_count: number
  delete_count: number
}

export interface DashboardData {
  stats: DashboardStats
  ci_type_distribution: CITypeStats[]
  environment_distribution: EnvironmentStats[]
  change_trend: ChangeTrend[]
  recent_changes: Array<{
    id: number
    ci_name: string
    change_type: string
    status: string
    created_at: string
    created_by: string
  }>
}

export function getDashboardData(): Promise<ApiResponse<DashboardData>> {
  return http.get<DashboardData>('/dashboard')
}

export interface RelationNode {
  id: number
  name: string
  ci_type: string
  status: string
}

export interface RelationEdge {
  source: number
  target: number
  relation_type: string
}

export interface RelationGraphData {
  nodes: RelationNode[]
  edges: RelationEdge[]
}

export function getRelationGraph(params?: {
  ci_id?: number
  depth?: number
}): Promise<ApiResponse<RelationGraphData>> {
  return http.get<RelationGraphData>('/relations/graph', { params })
}

export interface ReportData {
  ci_summary: {
    total: number
    by_type: Array<{ type: string; count: number }>
    by_status: Array<{ status: string; count: number }>
    by_environment: Array<{ environment: string; count: number }>
  }
  change_summary: {
    total: number
    by_status: Array<{ status: string; count: number }>
    by_type: Array<{ type: string; count: number }>
  }
  user_summary: {
    total: number
    active: number
    by_role: Array<{ role: string; count: number }>
  }
}

export function getReportData(params?: {
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<ReportData>> {
  return http.get<ReportData>('/reports/summary', { params })
}

export function exportReport(params?: {
  start_date?: string
  end_date?: string
  format?: 'pdf' | 'excel'
}): Promise<ApiResponse<string>> {
  return http.post<string>('/reports/export', params)
}
