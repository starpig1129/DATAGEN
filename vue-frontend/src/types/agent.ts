// 代理相關類型定義

export enum AgentType {
  PROCESS = 'PROCESS',
  HYPOTHESIS = 'HYPOTHESIS',
  SEARCH = 'SEARCH',
  CODE = 'CODE',
  VISUALIZATION = 'VISUALIZATION',
  REPORT = 'REPORT',
  QUALITY_REVIEW = 'QUALITY_REVIEW',
  REFINER = 'REFINER'
}

export enum AgentStatus {
  IDLE = 'IDLE',
  ACTIVE = 'ACTIVE',
  PROCESSING = 'PROCESSING',
  WAITING = 'WAITING',
  ERROR = 'ERROR'
}

export interface AgentPerformance {
  tasksCompleted: number
  averageResponseTime: number
  successRate: number
  lastUpdated: string
}

export interface Agent {
  id: string
  name: string
  type: AgentType
  status: AgentStatus
  currentTask?: string
  lastActivity: string
  performance?: AgentPerformance
  metadata?: Record<string, any>
}

export interface AgentStateUpdate {
  agentId: string
  changes: Partial<Agent>
  timestamp: string
}

export interface WorkflowState {
  id: string
  name: string
  status: 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'ERROR'
  currentStep: string
  totalSteps: number
  completedSteps: number
  startTime: string
  endTime?: string
  agents: string[]
}

export interface WorkflowProgress {
  workflowId: string
  stepName: string
  progress: number
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'ERROR'
  message?: string
  timestamp: string
}

// 代理任務相關
export interface AgentTask {
  id: string
  agentId: string
  type: string
  description: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  createdAt: string
  startedAt?: string
  completedAt?: string
  result?: any
  error?: string
}

// 代理協作相關
export interface AgentCollaboration {
  requestingAgent: string
  targetAgent: string
  requestType: string
  payload: any
  timestamp: string
}