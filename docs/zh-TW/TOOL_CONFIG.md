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

## 安全性與資源限制

### 配置檔案

工具限制設定於 `config/tool_limits.yaml`：

```yaml
# 執行限制
execution:
  timeout_seconds: 60              # 固定超時 (null = 無限制)
  max_memory_mb: 512               # 記憶體限制 (僅 Linux)
  max_output_chars: 50000          # 截斷輸出
  progress_timeout_seconds: 300    # ML/DL 任務用

# 檔案操作限制
file_operations:
  max_read_bytes: 5242880          # 5MB
  max_read_lines: 10000
  max_write_bytes: 10485760        # 10MB
  allowed_extensions: [.py, .md, .txt, .csv, .json]
  blocked_paths: [/etc, /sys, ~/.ssh]

# 全域開關
enable_security_scan: true
enable_write_validation: true
```

### execute_code 參數

```python
execute_code(
    input_code="...",
    codefile_name="code.py",
    timeout=60,              # 固定超時秒數
    memory_mb=512,           # 記憶體限制 (Linux)
    progress_timeout=300     # 無輸出時才超時
)
```

| 參數 | 類型 | 說明 |
|------|------|------|
| `timeout` | `int \| None` | N 秒後強制終止 |
| `memory_mb` | `int \| None` | 記憶體限制 (MB, 僅 Linux) |
| `progress_timeout` | `int \| None` | 僅在 N 秒無 stdout 時超時 |

> **提示**: ML/DL 訓練時，使用 `progress_timeout` 而非 `timeout`，允許有進度輸出的長時間任務。

### 安全功能

| 功能 | 說明 |
|------|------|
| **程式碼掃描** | AST 分析阻擋危險模式 (`eval`, `os.system` 等) |
| **路徑驗證** | 阻擋敏感路徑 (`/etc`, `~/.ssh`) |
| **內容驗證** | 警告未完成標記 (TODO, FIXME) |
| **大小限制** | 防止讀寫過大檔案 |

### 預設阻擋模式

```
os.system, subprocess.call, subprocess.run, subprocess.Popen,
shutil.rmtree, eval(, exec(, __import__
```

---

## Agent 工具配置

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

## 程式化存取

```python
from src.tools.factory import ToolFactory

# 取得目前配置
config = ToolFactory.get_config()

# 僅取得限制
limits = ToolFactory.get_limits()
print(limits["execution"]["timeout_seconds"])
```

---

## 回退機制

如果 `config.yaml` 中未定義 `tools`，系統會回退到 Agent 類別中的 `_get_tools()` 方法。

---

## 相關文檔
- [快速入門](QUICKSTART.md)
- [Agent 配置參考](AGENT_CONFIG.md)

