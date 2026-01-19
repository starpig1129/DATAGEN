# Agent Configuration Reference

This document details all agent configuration options.

## Directory Structure

Each agent's configuration is located at `config/agents/{agent_name}/`:

```
config/agents/{agent_name}/
├── AGENT.md       # System prompt (required)
└── config.yaml    # Capabilities config (required)
```

---

## AGENT.md Format

### YAML Frontmatter (Metadata)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique agent identifier (lowercase + hyphens) |
| `description` | string | ✅ | Brief description of agent's function |
| `version` | string | ❌ | Semantic version (default: 1.0.0) |
| `use_complete_prompt` | boolean | ❌ | If `true`, use complete prompt mode |

### Example

```markdown
---
name: code-agent
description: Python expert for data analysis code writing and execution
version: 1.2.0
---

# Code Agent

You are a Python programmer specializing in data processing...
```

---

## config.yaml Format

### Complete Structure

```yaml
# Tool list (string array)
tools:
  - execute_code
  - read_document

# Skill references (from config/skills/)
skills:
  - data-validation

# Rules file path
rules: _shared/rules.md

# MCP server list
mcp_servers:
  - filesystem
  - web-search
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `tools` | List[str] | Available tool names (see [Tool Configuration](TOOL_CONFIG.md)) |
| `skills` | List[str] | Referenced skill names (see [Skill Configuration](SKILL_CONFIG.md)) |
| `rules` | str | Rules file path (relative to `config/agents/`) |
| `mcp_servers` | List[str] | Enabled MCP server names |

---

## Loading Mechanism

### Progressive Disclosure

The system uses a three-level loading strategy to optimize Context Window:

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: Metadata                                          │
│  ─────────────────────────────────────────────────────────  │
│  • Loaded at system startup                                  │
│  • Contains only name, description                           │
│  • Very lightweight (~100 tokens)                            │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ (When agent is triggered)
┌─────────────────────────────────────────────────────────────┐
│  Level 2: Instructions                                       │
│  ─────────────────────────────────────────────────────────  │
│  • Full system prompt (AGENT.md content)                     │
│  • Auto-injected global rules                                │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ (When agent calls lookup_skill)
┌─────────────────────────────────────────────────────────────┐
│  Level 3: Resources                                          │
│  ─────────────────────────────────────────────────────────  │
│  • Full SKILL.md content                                     │
│  • MCP server resources                                      │
│  • External files                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation
- [Quick Start](QUICKSTART.md)
- [Tool Configuration](TOOL_CONFIG.md)
- [Skill Configuration](SKILL_CONFIG.md)
- [MCP Configuration](MCP_CONFIG.md)
