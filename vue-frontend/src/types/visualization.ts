// 數據視覺化相關類型定義

import type { PlotData, Layout, Config } from 'plotly.js'

export interface PlotlyData extends PlotData {}
export interface PlotlyLayout extends Partial<Layout> {}
export interface PlotlyConfig extends Partial<Config> {}

export enum ChartType {
  LINE = 'line',
  BAR = 'bar',
  SCATTER = 'scatter',
  PIE = 'pie',
  HEATMAP = 'heatmap',
  HISTOGRAM = 'histogram',
  BOX = 'box',
  VIOLIN = 'violin',
  SURFACE = 'surface',
  CONTOUR = 'contour'
}

export interface ChartData {
  id: string
  title: string
  type: ChartType
  data: PlotlyData[]
  layout?: PlotlyLayout
  config?: PlotlyConfig
  metadata?: ChartMetadata
}

export interface ChartMetadata {
  source?: string
  description?: string
  createdAt: string
  updatedAt: string
  tags?: string[]
  author?: string
}

export interface VisualizationState {
  charts: ChartData[]
  activeChartId?: string
  isLoading: boolean
  error?: string
}

// 圖表控制相關
export interface ChartControls {
  showLegend: boolean
  showGrid: boolean
  showToolbar: boolean
  theme: 'light' | 'dark'
  colorScheme?: string
  animation: boolean
}

export interface ChartFilter {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains'
  value: any
}

export interface ChartQuery {
  dataSource: string
  fields: string[]
  filters?: ChartFilter[]
  groupBy?: string[]
  orderBy?: Array<{
    field: string
    direction: 'asc' | 'desc'
  }>
  limit?: number
}

// 數據處理相關
export interface DataTransformation {
  type: 'aggregate' | 'filter' | 'sort' | 'pivot' | 'join'
  config: Record<string, any>
}

export interface Dataset {
  id: string
  name: string
  data: Record<string, any>[]
  schema: DataSchema
  transformations?: DataTransformation[]
}

export interface DataSchema {
  fields: Array<{
    name: string
    type: 'number' | 'string' | 'date' | 'boolean'
    nullable?: boolean
    description?: string
  }>
}

// 儀表板相關
export interface Dashboard {
  id: string
  name: string
  description?: string
  layout: DashboardLayout
  charts: string[]
  filters?: DashboardFilter[]
  settings: DashboardSettings
}

export interface DashboardLayout {
  type: 'grid' | 'flex'
  columns: number
  gap: number
  items: Array<{
    chartId: string
    position: {
      x: number
      y: number
      width: number
      height: number
    }
  }>
}

export interface DashboardFilter {
  id: string
  type: 'dropdown' | 'slider' | 'daterange' | 'text'
  field: string
  label: string
  options?: any[]
  value?: any
}

export interface DashboardSettings {
  autoRefresh: boolean
  refreshInterval?: number
  theme: 'light' | 'dark'
  responsive: boolean
}

// 導出相關
export interface ExportOptions {
  format: 'png' | 'jpg' | 'pdf' | 'svg' | 'html'
  width?: number
  height?: number
  scale?: number
  quality?: number
}

export interface ExportResult {
  success: boolean
  url?: string
  error?: string
}