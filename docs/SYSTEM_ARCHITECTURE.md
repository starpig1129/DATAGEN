# System Architecture & Configuration Guide

This document details the advanced **Agent Configuration System** and **Progressive Disclosure Architecture** implemented in DATAGEN.

## 1. Architecture Overview (Progressive Disclosure)

To optimize Context Window usage and system performance, DATAGEN employs a **Progressive Disclosure** strategy for agent knowledge and capabilities.

| Level | Component | Description | Load Time |
|-------|-----------|-------------|-----------|
| **Level 1** | **Metadata** | Basic agent info (name, desc, available skills/tools) | System Startup (Lightweight) |
| **Level 2** | **Instructions** | Full System Prompt (AGENT.md) + Rules | On Agent Trigger |
| **Level 3** | **Skills & Resources** | Detailed Skill content (`SKILL.md`) and MCP Resources | On Demand (via Tool Call) |

---

## 2. Directory Structure

Configuration is centralized in the `config/` directory:

```plaintext
config/
├── agent_models.yaml          # LLM Provider & Model settings
├── mcp.yaml                   # Model Context Protocol (MCP) Server config
├── skills/                    # Shared Skills Repository
│   └── {skill-name}/
│       └── SKILL.md           # Reusable Skill Definition
│
└── agents/                    # Agent-Specific Configurations
    ├── _shared/               # Global shared resources
    │   └── rules.md           # Global Operational Rules
    │
    └── {agent_name}/          # Individual Agent Config
        ├── AGENT.md           # System Prompt (Markdown + Frontmatter)
        └── config.yaml        # Tools, Skills, and MCP settings
```

---

## 3. Agent Configuration

Each agent is defined by two files in `config/agents/{agent_name}/`:

### `AGENT.md` (System Prompt)
Uses YAML frontmatter for metadata and Markdown for the prompt logic.

```markdown
---
name: process-agent
description: Research supervisor for data analysis projects.
version: 1.0.0
---

# Process Agent Role
You are the supervisor...
```

### `config.yaml` (Capabilities)
Defines what the agent can *do* (Tools) and what it *knows* (Skills).

```yaml
tools:
  - execute_code        # Python execution
  - read_document       # File reading
  - wikipedia           # Complex tool (auto-initialized)
  - arxiv               # External library tool

skills:
  - data-validation     # References config/skills/data-validation/SKILL.md

mcp_servers:
  - filesystem          # Enable MCP server access
```

---

## 4. Skills System

Skills are reusable "knowledge modules" stored in `config/skills/`.

### Creating a New Skill
1. Create folder: `config/skills/my-new-skill/`
2. Create `SKILL.md`:

```markdown
---
name: my-new-skill
description: Evaluating data quality against standard metrics.
---

# Data Quality Standards
1. Completeness: Check for missing values...
2. Consistency: Verify data types...
```

### Using a Skill
Add it to the agent's `config.yaml`:
```yaml
skills:
  - my-new-skill
```

The agent will initially see only the **description**. If it needs the details, it uses the `lookup_skill` tool to read the full content.

---

## 5. Tool Configuration

Tools are managed by the `ToolFactory`. Available tools include:

- **Core**: `execute_code`, `execute_command`, `list_directory`
- **FileOps**: `read_document`, `create_document`, `edit_document`
- **Research**: `wikipedia`, `arxiv`, `google_search`, `scrape_webpages`
- **System**: `lookup_skill` (Auto-added if skills are present)

To add tools to an agent, simply list them in `config.yaml`.

---

## 6. Model Context Protocol (MCP)

MCP Servers allow safe interaction with external systems (Filesystem, GitHub, Web Search).

### Configuration (`config/mcp.yaml`)
```yaml
servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
  
defaults:
  - filesystem  # Enabled for all agents by default
```

Agents can override or add servers in their specific `config.yaml`.

---

## 7. Global Rules

Global operational rules (e.g., Coding Standards, Ethics) are defined in `config/agents/_shared/rules.md`. These are automatically injected into every agent's system prompt during loading.
