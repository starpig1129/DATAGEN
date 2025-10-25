/**
 * 報告相關類型定義
 * 基於 Google TypeScript Style Guide
 */

/** 報告內容塊類型 */
export type ReportBlockType = 
  | 'text'
  | 'heading'
  | 'image'
  | 'chart'
  | 'table'
  | 'divider'
  | 'code'
  | 'quote';

/** 報告內容塊基礎介面 */
export interface ReportBlockBase {
  id: string;
  type: ReportBlockType;
  order: number;
  createdAt: string;
  updatedAt: string;
}

/** 文本塊 */
export interface TextBlock extends ReportBlockBase {
  type: 'text';
  content: string;
  formatting?: {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    fontSize?: number;
    color?: string;
    align?: 'left' | 'center' | 'right' | 'justify';
  };
}

/** 標題塊 */
export interface HeadingBlock extends ReportBlockBase {
  type: 'heading';
  content: string;
  level: 1 | 2 | 3 | 4 | 5 | 6;
  numbering?: boolean;
}

/** 圖片塊 */
export interface ImageBlock extends ReportBlockBase {
  type: 'image';
  src: string;
  alt: string;
  caption?: string;
  width?: number;
  height?: number;
  align?: 'left' | 'center' | 'right';
}

/** 圖表塊 */
export interface ChartBlock extends ReportBlockBase {
  type: 'chart';
  chartId: string;
  chartType: string;
  title?: string;
  caption?: string;
  config?: Record<string, any>;
}

/** 表格塊 */
export interface TableBlock extends ReportBlockBase {
  type: 'table';
  headers: string[];
  rows: string[][];
  caption?: string;
  styling?: {
    headerStyle?: Record<string, string>;
    cellStyle?: Record<string, string>;
    bordered?: boolean;
    striped?: boolean;
  };
}

/** 分隔線塊 */
export interface DividerBlock extends ReportBlockBase {
  type: 'divider';
  style?: 'solid' | 'dashed' | 'dotted';
  thickness?: number;
}

/** 代碼塊 */
export interface CodeBlock extends ReportBlockBase {
  type: 'code';
  content: string;
  language?: string;
  showLineNumbers?: boolean;
}

/** 引用塊 */
export interface QuoteBlock extends ReportBlockBase {
  type: 'quote';
  content: string;
  author?: string;
  source?: string;
}

/** 聯合類型 - 所有報告塊類型 */
export type ReportBlock = 
  | TextBlock
  | HeadingBlock
  | ImageBlock
  | ChartBlock
  | TableBlock
  | DividerBlock
  | CodeBlock
  | QuoteBlock;

/** 報告元數據 */
export interface ReportMetadata {
  title: string;
  author: string;
  description?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  version: number;
  language: string;
  template?: string;
}

/** 報告樣式配置 */
export interface ReportStyle {
  theme: 'default' | 'academic' | 'business' | 'minimal';
  fontFamily: string;
  fontSize: number;
  lineHeight: number;
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  colors: {
    primary: string;
    secondary: string;
    text: string;
    background: string;
    border: string;
  };
  pageSize: 'A4' | 'A3' | 'Letter' | 'Legal';
  orientation: 'portrait' | 'landscape';
}

/** 完整報告結構 */
export interface Report {
  id: string;
  metadata: ReportMetadata;
  style: ReportStyle;
  blocks: ReportBlock[];
  tableOfContents: boolean;
  pageNumbers: boolean;
  watermark?: string;
}

/** 報告模板 */
export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: 'academic' | 'business' | 'technical' | 'custom';
  preview: string;
  style: ReportStyle;
  defaultBlocks: Partial<ReportBlock>[];
  variables?: Record<string, string>;
}

/** 導出選項 */
export interface ExportOptions {
  format: 'pdf' | 'docx' | 'html' | 'markdown';
  quality: 'draft' | 'standard' | 'high';
  includeImages: boolean;
  includeCharts: boolean;
  watermark?: string;
  password?: string;
  metadata?: Record<string, string>;
}

/** API 響應類型 */
export interface ReportApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

/** 報告列表項目 */
export interface ReportListItem {
  id: string;
  title: string;
  author: string;
  description?: string;
  thumbnail?: string;
  createdAt: string;
  updatedAt: string;
  status: 'draft' | 'published' | 'archived';
  tags: string[];
}

/** 報告操作歷史 */
export interface ReportOperation {
  id: string;
  reportId: string;
  operation: 'create' | 'update' | 'delete' | 'export' | 'share';
  details: string;
  timestamp: string;
  userId?: string;
}

/** 報告分享設定 */
export interface ReportSharingSettings {
  isPublic: boolean;
  allowComments: boolean;
  allowDownload: boolean;
  expiresAt?: string;
  password?: string;
  permissions: {
    view: boolean;
    edit: boolean;
    share: boolean;
  };
}