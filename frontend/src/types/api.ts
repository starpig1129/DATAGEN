// API相關類型定義

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: 'success' | 'error' | 'processing'
  message?: string
}

export interface PaginationParams {
  limit?: number
  offset?: number
  page?: number
  pageSize?: number
}

export interface SortParams {
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface FilterParams {
  search?: string
  filters?: Record<string, any>
}

export interface QueryParams extends PaginationParams, SortParams, FilterParams {}

// GraphQL相關類型
export interface GraphQLError {
  message: string
  extensions?: {
    code?: string
    path?: string[]
  }
}

export interface GraphQLResponse<T = any> {
  data?: T
  errors?: GraphQLError[]
}

// WebSocket相關類型
export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: number
}

export interface SSEEvent {
  type: string
  data: string
  id?: string
  retry?: number
}