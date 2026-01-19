# 工具配置指南

本文檔說明如何為 Agent 配置工具。

## 概述

工具 (Tools) 是 Agent 與外部世界交互的能力。所有工具由 `ToolFactory` 集中管理。

---

## 可用工具列表

### 核心工具

| 工具名稱 | 說明 | 用途 |
|----------|------|------|
| `execute_code` | 執行 Python 代碼 | 數據處理、分析 |
| `execute_command` | 執行 Shell 命令 | 系統操作 |
| `list_directory` | 列出目錄內容 | 檔案探索 |

### 文件操作工具

| 工具名稱 | 說明 | 用途 |
|----------|------|------|
| `read_document` | 讀取文件內容 | 讀取數據、報告 |
| `create_document` | 創建新文件 | 生成報告 |
| `edit_document` | 編輯現有文件 | 修改內容 |
| `collect_data` | 收集數據 | 數據匯整 |

### 研究工具

| 工具名稱 | 說明 | 用途 |
|----------|------|------|
| `wikipedia` | 查詢 Wikipedia | 背景知識 |
| `arxiv` | 查詢 arXiv 論文 | 學術研究 |
| `google_search` | Google 搜尋 | 網路資訊 |
| `scrape_webpages` | 網頁抓取 | 網頁內容提取 |

### 系統工具

| 工具名稱 | 說明 | 用途 |
|----------|------|------|
| `lookup_skill` | 查詢技能內容 | 自動添加 (若配置 skills) |

---

## 配置方式

### 在 config.yaml 中指定

```yaml
tools:
  - execute_code
  - read_document
  - wikipedia
```

### 配置範例

#### Code Agent
```yaml
tools:
  - execute_code
  - execute_command
  - read_document
  - list_directory
```

#### Search Agent
```yaml
tools:
  - read_document
  - wikipedia
  - arxiv
  - google_search
  - scrape_webpages
  - list_directory
```

#### Report Agent
```yaml
tools:
  - create_document
  - read_document
  - edit_document
  - list_directory
```

---

## 自定義工具

### 添加新工具到 ToolFactory

1. 在 `src/tools/` 中創建工具函數
2. 在 `src/tools/factory.py` 中註冊：

```python
from .my_tools import my_custom_tool

class ToolFactory:
    _registry = {
        # ... 現有工具 ...
        "my_custom_tool": my_custom_tool,
    }
```

3. 在 Agent 的 `config.yaml` 中引用：
```yaml
tools:
  - my_custom_tool
```

---

## 回退機制

如果 `config.yaml` 中未定義 `tools`，系統會回退到 Agent 類別中的 `_get_tools()` 方法。

---

## 相關文檔
- [快速入門](QUICKSTART.md)
- [Agent 配置參考](AGENT_CONFIG.md)
