// 文件管理相關類型定義

export interface FileInfo {
  id: string
  name: string
  path: string
  size: number
  type: string
  extension: string
  mimeType: string
  createdAt: string
  updatedAt: string
  createdBy?: string
  tags?: string[]
  metadata?: Record<string, any>
}

export interface FilePreview {
  id: string
  content: string
  contentType: 'text' | 'image' | 'pdf' | 'binary'
  encoding?: string
  thumbnail?: string
}

export interface FileUploadInput {
  file: File
  path?: string
  tags?: string[]
  metadata?: Record<string, any>
}

export interface FileUploadProgress {
  fileId: string
  fileName: string
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

export interface FileSearchParams {
  query?: string
  path?: string
  type?: string
  extension?: string
  tags?: string[]
  dateRange?: {
    start: string
    end: string
  }
  sizeRange?: {
    min: number
    max: number
  }
}

export interface FileOperation {
  type: 'copy' | 'move' | 'delete' | 'rename'
  fileIds: string[]
  targetPath?: string
  newName?: string
}

export interface FileOperationResult {
  success: boolean
  message?: string
  affectedFiles: string[]
  errors?: Array<{
    fileId: string
    error: string
  }>
}

// 文件系統相關
export interface DirectoryTree {
  path: string
  name: string
  type: 'file' | 'directory'
  children?: DirectoryTree[]
  size?: number
  fileCount?: number
}

export interface FilePermission {
  read: boolean
  write: boolean
  delete: boolean
  share: boolean
}

// 文件版本管理
export interface FileVersion {
  id: string
  fileId: string
  version: string
  size: number
  createdAt: string
  createdBy: string
  changelog?: string
}