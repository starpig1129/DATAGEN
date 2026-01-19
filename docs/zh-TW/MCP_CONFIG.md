# MCP 服務配置指南

本文檔說明如何配置 Model Context Protocol (MCP) 服務。

## 概述

MCP (Model Context Protocol) 是一種標準化協議，允許 Agent 安全地與外部系統交互，例如：
- 檔案系統操作
- GitHub 倉庫存取
- 網頁搜尋
- 資料庫查詢

---

## 全域配置

### 文件位置

MCP 服務在 `config/mcp.yaml` 中集中定義：

```yaml
servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
    
  web-search:
    command: npx
    args: ["-y", "@anthropic/mcp-server-web-search"]
    
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"

defaults:
  - filesystem   # 所有 Agent 預設啟用
```

### 配置結構

| 欄位 | 說明 |
|------|------|
| `servers` | 所有可用的 MCP 服務定義 |
| `servers.{name}.command` | 啟動服務的命令 |
| `servers.{name}.args` | 命令參數 |
| `servers.{name}.env` | 環境變數 |
| `defaults` | 所有 Agent 預設啟用的服務 |

---

## 環境變數

支援 `${VAR_NAME}` 語法引用環境變數：

```yaml
servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
```

系統會自動從 `.env` 或系統環境變數中讀取 `WORKING_DIRECTORY` 的值。

---

## Agent 特定配置

### 在 config.yaml 中啟用

除了全域 `defaults`，每個 Agent 可以額外啟用服務：

```yaml
# config/agents/search_agent/config.yaml
mcp_servers:
  - web-search
  - github
```

### 最終效果

Agent 實際啟用的服務 = `defaults` ∪ Agent 特定 `mcp_servers`

---

## 常用 MCP 服務

### Filesystem

```yaml
filesystem:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
```

功能：讀取、寫入、列出目錄內容

### Web Search

```yaml
web-search:
  command: npx
  args: ["-y", "@anthropic/mcp-server-web-search"]
```

功能：執行網頁搜尋

### GitHub

```yaml
github:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

功能：存取 GitHub 倉庫、Issues、PR

---

## 安全考量

> [!WARNING]
> MCP 服務具有強大的系統存取能力。請確保：
> - 只啟用必要的服務
> - 妥善保管 API Token
> - 限制檔案系統存取範圍

---

## 相關文檔
- [快速入門](QUICKSTART.md)
- [Agent 配置參考](AGENT_CONFIG.md)
