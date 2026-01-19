# System Architecture Overview

This document provides a high-level overview of the DATAGEN system architecture.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Quick Start](QUICKSTART.md) | Configure an agent in 5 minutes |
| [Agent Configuration](AGENT_CONFIG.md) | Complete AGENT.md and config.yaml reference |
| [Tool Configuration](TOOL_CONFIG.md) | Available tools and custom tool guide |
| [Skill Configuration](SKILL_CONFIG.md) | Create and use reusable knowledge modules |
| [MCP Configuration](MCP_CONFIG.md) | Model Context Protocol server setup |

---

## Core Concepts

### Progressive Disclosure

DATAGEN uses a three-level loading strategy to optimize Context Window usage:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Level 1: Metadata                 ← Loaded at startup (~100 tokens) │
│   ─────────────────                                             │
│   • Agent name, description                                     │
│   • Available skills list (names only)                          │
│                                                                 │
│             ▼                                                   │
│                                                                 │
│   Level 2: Instructions             ← Loaded when agent triggered │
│   ─────────────────                                             │
│   • Full AGENT.md content                                       │
│   • Auto-injected global rules                                  │
│                                                                 │
│             ▼                                                   │
│                                                                 │
│   Level 3: Resources                ← Loaded on demand (via lookup_skill) │
│   ─────────────────                                             │
│   • Full SKILL.md content                                       │
│   • MCP server resources                                        │
│   • External files                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Design Philosophy

This architecture is inspired by [Claude Agent Skills](https://platform.claude.com/docs/agents-and-tools/agent-skills/overview), ensuring:

1. **Minimal Startup Cost**: Only lightweight metadata loaded at startup
2. **On-Demand Loading**: Detailed instructions enter Context Window only when needed
3. **Composability**: Skills can be shared across multiple agents

---

## Directory Structure

```plaintext
config/
├── agent_models.yaml          # LLM Provider and model settings
├── mcp.yaml                   # MCP server global configuration
│
├── skills/                    # Shared skills repository
│   └── {skill-name}/
│       └── SKILL.md
│
└── agents/                    # Agent-specific configurations
    ├── _shared/
    │   └── rules.md           # Global rules (auto-injected)
    │
    └── {agent_name}/
        ├── AGENT.md           # System prompt
        └── config.yaml        # Tools, skills, MCP settings
```

---

## Core Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| AgentConfigLoader | `src/core/agent_config_loader.py` | Load agent configs with progressive disclosure |
| ToolFactory | `src/tools/factory.py` | Tool registration and dynamic loading |
| MCPManager | `src/core/mcp_manager.py` | MCP server lifecycle management |
| BaseAgent | `src/agents/base.py` | Agent base class with config integration |

---

## Next Steps

- 👉 [Quick Start](QUICKSTART.md) - Start configuring your first agent
