# 技能配置指南

本文檔說明如何創建和使用 Agent Skills。

## 概述

Skills (技能) 是可重用的知識模組，為 Agent 提供特定領域的專業知識。Skills 採用**漸進式揭露**：Agent 最初只看到描述，需要時才載入完整內容。

---

## 目錄結構

所有技能存放於 `config/skills/`：

```
config/skills/
└── {skill-name}/
    └── SKILL.md       # 技能定義文件 (必需)
```

---

## SKILL.md 格式

### 基本結構

```markdown
---
name: skill-name
description: 簡短描述此技能的功能及使用時機
---

# 技能標題

## 指令
[Agent 應遵循的步驟]

## 最佳實踐
[推薦的工作方式]

## 範例
[具體使用範例]
```

### 欄位要求

| 欄位 | 要求 | 說明 |
|------|------|------|
| `name` | 必需，最多 64 字元 | 小寫字母、數字、連字號 |
| `description` | 必需，最多 1024 字元 | 描述功能與觸發條件 |

---

## 創建技能教學

### 範例：數據驗證技能

1. 創建目錄：
```bash
mkdir -p config/skills/data-validation
```

2. 創建 `config/skills/data-validation/SKILL.md`：

```markdown
---
name: data-validation
description: 驗證數據集的完整性與一致性。當需要檢查數據質量、識別缺失值或驗證數據類型時使用。
---

# 數據驗證

## 驗證步驟

1. **完整性檢查**
   - 識別缺失值 (`df.isnull().sum()`)
   - 計算缺失比例

2. **一致性檢查**
   - 驗證數據類型
   - 檢查值域範圍

3. **唯一性檢查**
   - 識別重複記錄
   - 驗證主鍵唯一性

## 範例代碼

\`\`\`python
import pandas as pd

def validate_dataset(df: pd.DataFrame) -> dict:
    return {
        "missing": df.isnull().sum().to_dict(),
        "duplicates": df.duplicated().sum(),
        "dtypes": df.dtypes.to_dict()
    }
\`\`\`
```

---

## 使用技能

### 在 Agent config.yaml 中引用

```yaml
skills:
  - data-validation
```

### 運作機制

1. **Level 1 (系統啟動)**：Agent 僅知道技能的 `name` 和 `description`
2. **Level 2 (需要時)**：Agent 呼叫 `lookup_skill("data-validation")` 獲取完整內容

這種設計避免了不必要的 Context Window 消耗。

---

## 進階：多文件技能

技能可以包含多個文件：

```
config/skills/advanced-skill/
├── SKILL.md           # 主指令文件
├── REFERENCE.md       # 詳細參考
└── scripts/
    └── helper.py      # 輔助腳本
```

在 `SKILL.md` 中引用其他文件：
```markdown
如需詳細 API 參考，請參閱 [REFERENCE.md](REFERENCE.md)。
```

---

## 相關文檔
- [快速入門](QUICKSTART.md)
- [Agent 配置參考](AGENT_CONFIG.md)
