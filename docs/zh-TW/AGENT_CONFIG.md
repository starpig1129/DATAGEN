# Agent 配置參考

本文檔詳細說明 Agent 配置的所有選項。

## 目錄結構

每個 Agent 的配置位於 `config/agents/{agent_name}/`：

```
config/agents/{agent_name}/
├── AGENT.md       # 系統提示詞 (必需)
└── config.yaml    # 能力配置 (必需)
```

---

## AGENT.md 格式

### YAML Frontmatter (元數據)

| 欄位 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `name` | string | ✅ | Agent 唯一識別符 (小寫+連字號) |
| `description` | string | ✅ | 簡短描述 Agent 的功能 |
| `version` | string | ❌ | 語義版本號 (預設: 1.0.0) |
| `use_complete_prompt` | boolean | ❌ | 若為 `true`，使用完整提示詞模式 |

### 範例

```markdown
---
name: code-agent
description: Python 專家，負責數據分析代碼的編寫與執行
version: 1.2.0
---

# Code Agent

您是一位專精於數據處理的 Python 程式設計師...
```

---

## config.yaml 格式

### 完整結構

```yaml
# 工具列表 (字串陣列)
tools:
  - execute_code
  - read_document

# 技能引用 (來自 config/skills/)
skills:
  - data-validation

# 規則文件路徑
rules: _shared/rules.md

# MCP 服務列表
mcp_servers:
  - filesystem
  - web-search
```

### 欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `tools` | List[str] | 可用工具名稱 (見 [工具配置](TOOL_CONFIG.md)) |
| `skills` | List[str] | 引用的技能名稱 (見 [技能配置](SKILL_CONFIG.md)) |
| `rules` | str | 規則文件路徑 (相對於 `config/agents/`) |
| `mcp_servers` | List[str] | 啟用的 MCP 服務名稱 |

---

## 載入機制

### 漸進式揭露 (Progressive Disclosure)

系統採用三級載入策略優化 Context Window：

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: 元數據                                            │
│  ─────────────────────────────────────────────────────────  │
│  • 系統啟動時載入                                            │
│  • 僅包含 name, description                                 │
│  • 極輕量 (~100 tokens)                                     │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ (Agent 被觸發時)
┌─────────────────────────────────────────────────────────────┐
│  Level 2: 指令                                              │
│  ─────────────────────────────────────────────────────────  │
│  • 完整系統提示詞 (AGENT.md 內容)                            │
│  • 自動注入全域規則                                          │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ (Agent 呼叫 lookup_skill 時)
┌─────────────────────────────────────────────────────────────┐
│  Level 3: 資源                                              │
│  ─────────────────────────────────────────────────────────  │
│  • 完整 SKILL.md 內容                                        │
│  • MCP 服務資源                                              │
│  • 外部文件                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 相關文檔
- [快速入門](QUICKSTART.md)
- [工具配置](TOOL_CONFIG.md)
- [技能配置](SKILL_CONFIG.md)
- [MCP 服務配置](MCP_CONFIG.md)
