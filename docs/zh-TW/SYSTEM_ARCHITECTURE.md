# 系統架構概覽

本文檔提供 DATAGEN 系統架構的高階概覽。

## 文檔索引

| 文檔 | 說明 |
|------|------|
| [快速入門](QUICKSTART.md) | 5 分鐘內配置 Agent |
| [Agent 配置](AGENT_CONFIG.md) | AGENT.md 與 config.yaml 完整參考 |
| [工具配置](TOOL_CONFIG.md) | 所有可用工具與自定義工具指南 |
| [技能配置](SKILL_CONFIG.md) | 創建與使用可重用知識模組 |
| [MCP 服務配置](MCP_CONFIG.md) | Model Context Protocol 服務設定 |

---

## 核心概念

### 漸進式揭露 (Progressive Disclosure)

DATAGEN 採用三級載入策略，優化 Context Window 使用效率：

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Level 1: 元數據                   ← 系統啟動時載入 (~100 tokens) │
│   ───────────────                                               │
│   • Agent 名稱、描述                                             │
│   • 可用技能列表 (僅名稱)                                         │
│                                                                 │
│             ▼                                                   │
│                                                                 │
│   Level 2: 指令                     ← Agent 被觸發時載入          │
│   ───────────────                                               │
│   • 完整 AGENT.md 內容                                           │
│   • 自動注入全域規則                                              │
│                                                                 │
│             ▼                                                   │
│                                                                 │
│   Level 3: 資源                     ← 按需載入 (via lookup_skill) │
│   ───────────────                                               │
│   • SKILL.md 完整內容                                            │
│   • MCP 服務資源                                                 │
│   • 外部檔案                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 設計理念

此架構參考了 [Claude Agent Skills](https://platform.claude.com/docs/agents-and-tools/agent-skills/overview) 規範，確保：

1. **最小化啟動成本**：系統啟動時僅載入輕量元數據
2. **按需載入**：詳細指令只在必要時進入 Context Window
3. **可組合性**：Skills 可在多個 Agent 間共用

---

## 目錄結構

```plaintext
config/
├── agent_models.yaml          # LLM Provider 與模型設定
├── mcp.yaml                   # MCP 服務全域配置
│
├── skills/                    # 共用技能庫
│   └── {skill-name}/
│       └── SKILL.md
│
└── agents/                    # Agent 專屬配置
    ├── _shared/
    │   └── rules.md           # 全域規則 (自動注入)
    │
    └── {agent_name}/
        ├── AGENT.md           # 系統提示詞
        └── config.yaml        # 工具、技能、MCP 設定
```

---

## 核心模組

| 模組 | 路徑 | 職責 |
|------|------|------|
| AgentConfigLoader | `src/core/agent_config_loader.py` | 載入 Agent 配置與漸進式揭露 |
| ToolFactory | `src/tools/factory.py` | 工具註冊與動態載入 |
| MCPManager | `src/core/mcp_manager.py` | MCP 服務生命週期管理 |
| BaseAgent | `src/agents/base.py` | Agent 基底類別與配置整合 |

---

## 下一步

- 👉 [快速入門](QUICKSTART.md) - 開始配置您的第一個 Agent
