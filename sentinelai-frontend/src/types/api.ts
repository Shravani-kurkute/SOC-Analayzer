export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
  errors: string[] | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface APIError {
  success: false;
  errorCode: string;
  message: string;
  details: Record<string, unknown> | null;
  requestId: string | null;
}

export interface WebSocketMessage {
  type: string;
  channel: string;
  payload: unknown;
  timestamp: string;
}
