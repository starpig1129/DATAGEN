/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GRAPHQL_HTTP_URL: string
  readonly VITE_GRAPHQL_WS_URL: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly BASE_URL: string
  readonly DEV: boolean
  readonly PROD: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
  readonly hot?: {
    accept(): void
    accept(cb: (mod: any) => void): void
    accept(dep: string, cb: (mod: any) => void): void
  }
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'plotly.js' {
  export interface PlotData {
    x?: any[]
    y?: any[]
    z?: any[]
    type?: string
    mode?: string
    name?: string
    marker?: any
    line?: any
    [key: string]: any
  }

  export interface Layout {
    title?: string | { text: string }
    xaxis?: any
    yaxis?: any
    showlegend?: boolean
    width?: number
    height?: number
    [key: string]: any
  }

  export interface Config {
    responsive?: boolean
    displayModeBar?: boolean
    displaylogo?: boolean
    modeBarButtonsToRemove?: string[]
    [key: string]: any
  }

  export function newPlot(
    div: HTMLElement,
    data: PlotData[],
    layout?: Partial<Layout>,
    config?: Partial<Config>
  ): Promise<void>

  export function react(
    div: HTMLElement,
    data: PlotData[],
    layout?: Partial<Layout>,
    config?: Partial<Config>
  ): Promise<void>

  export function redraw(div: HTMLElement): Promise<void>
  export function purge(div: HTMLElement): void
}

declare module 'vue-plotly' {
  import { DefineComponent } from 'vue'
  const VuePlotly: DefineComponent<any, any, any>
  export default VuePlotly
}