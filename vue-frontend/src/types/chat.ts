// 聊天相關類型定義

export enum MessageType {
  USER = 'USER',
  AGENT = 'AGENT',
  SYSTEM = 'SYSTEM',
  DECISION_REQUEST = 'DECISION_REQUEST'
}

export enum DecisionType {
  REGENERATE_HYPOTHESIS = 'REGENERATE_HYPOTHESIS',
  CONTINUE_RESEARCH = 'CONTINUE_RESEARCH',
  APPROVE_REPORT = 'APPROVE_REPORT',
  REQUEST_REVISION = 'REQUEST_REVISION'
}

export interface MessageMetadata {
  agentType?: string
  confidence?: number
  processingTime?: number
  sources?: readonly string[]
  attachments?: readonly string[]
}

export interface Message {
  id: string
  content: string
  sender: string
  timestamp: string
  type: MessageType
  metadata?: MessageMetadata
}

export interface ChatState {
  messages: Message[]
  isProcessing: boolean
  needsDecision: boolean
  currentTypingAgent?: string
  lastMessageId?: string
}

export interface SendMessageInput {
  content: string
  type?: MessageType
  metadata?: MessageMetadata
}

export interface DecisionInput {
  decision: DecisionType
  context?: string
  messageId?: string
}

export interface DecisionResult {
  success: boolean
  message?: string
  nextAction?: string
}

// 聊天UI相關
export interface ChatUIState {
  isInputDisabled: boolean
  showDecisionButtons: boolean
  isScrolledToBottom: boolean
  unreadCount: number
}

// 輸入框狀態
export interface InputState {
  text: string
  isComposing: boolean
  placeholder: string
  maxLength: number
}

// 決策按鈕配置
export interface DecisionButton {
  type: DecisionType
  label: string
  variant: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  icon?: string
  disabled?: boolean
}