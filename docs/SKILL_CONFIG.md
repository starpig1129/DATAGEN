# Skill Configuration Guide

This document explains how to create and use Agent Skills.

## Overview

Skills are reusable knowledge modules that provide agents with domain-specific expertise. Skills use **progressive disclosure**: agents initially see only the description, loading full content only when needed.

---

## Directory Structure

All skills are stored in `config/skills/`:

```
config/skills/
└── {skill-name}/
    └── SKILL.md       # Skill definition file (required)
```

---

## SKILL.md Format

### Basic Structure

```markdown
---
name: skill-name
description: Brief description of the skill's function and when to use it
---

# Skill Title

## Instructions
[Steps the agent should follow]

## Best Practices
[Recommended approaches]

## Examples
[Concrete usage examples]
```

### Field Requirements

| Field | Requirement | Description |
|-------|-------------|-------------|
| `name` | Required, max 64 chars | Lowercase letters, numbers, hyphens |
| `description` | Required, max 1024 chars | Describes function and trigger conditions |

---

## Creating a Skill Tutorial

### Example: Data Validation Skill

1. Create directory:
```bash
mkdir -p config/skills/data-validation
```

2. Create `config/skills/data-validation/SKILL.md`:

```markdown
---
name: data-validation
description: Validate dataset completeness and consistency. Use when checking data quality, identifying missing values, or verifying data types.
---

# Data Validation

## Validation Steps

1. **Completeness Check**
   - Identify missing values (`df.isnull().sum()`)
   - Calculate missing ratio

2. **Consistency Check**
   - Verify data types
   - Check value ranges

3. **Uniqueness Check**
   - Identify duplicate records
   - Verify primary key uniqueness

## Example Code

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

## Using Skills

### Reference in Agent config.yaml

```yaml
skills:
  - data-validation
```

### How It Works

1. **Level 1 (System Startup)**: Agent only knows the skill's `name` and `description`
2. **Level 2 (When Needed)**: Agent calls `lookup_skill("data-validation")` to get full content

This design avoids unnecessary Context Window consumption.

---

## Advanced: Multi-File Skills

Skills can contain multiple files:

```
config/skills/advanced-skill/
├── SKILL.md           # Main instruction file
├── REFERENCE.md       # Detailed reference
└── scripts/
    └── helper.py      # Helper scripts
```

Reference other files in `SKILL.md`:
```markdown
For detailed API reference, see [REFERENCE.md](REFERENCE.md).
```

---

## Related Documentation
- [Quick Start](QUICKSTART.md)
- [Agent Configuration Reference](AGENT_CONFIG.md)
