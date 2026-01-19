# MCP Configuration Guide

This document explains how to configure Model Context Protocol (MCP) services.

## Overview

MCP (Model Context Protocol) is a standardized protocol that allows agents to safely interact with external systems, such as:
- File system operations
- GitHub repository access
- Web search
- Database queries

---

## Global Configuration

### File Location

MCP services are centrally defined in `config/mcp.yaml`:

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
  - filesystem   # Enabled for all agents by default
```

### Configuration Structure

| Field | Description |
|-------|-------------|
| `servers` | All available MCP service definitions |
| `servers.{name}.command` | Command to start the service |
| `servers.{name}.args` | Command arguments |
| `servers.{name}.env` | Environment variables |
| `defaults` | Services enabled for all agents by default |

---

## Environment Variables

Supports `${VAR_NAME}` syntax for referencing environment variables:

```yaml
servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
```

The system automatically reads `WORKING_DIRECTORY` from `.env` or system environment variables.

---

## Agent-Specific Configuration

### Enable in config.yaml

In addition to global `defaults`, each agent can enable additional services:

```yaml
# config/agents/search_agent/config.yaml
mcp_servers:
  - web-search
  - github
```

### Final Result

Agent's enabled services = `defaults` ∪ Agent-specific `mcp_servers`

---

## Common MCP Services

### Filesystem

```yaml
filesystem:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-filesystem", "${WORKING_DIRECTORY}"]
```

Capabilities: Read, write, list directory contents

### Web Search

```yaml
web-search:
  command: npx
  args: ["-y", "@anthropic/mcp-server-web-search"]
```

Capabilities: Perform web searches

### GitHub

```yaml
github:
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

Capabilities: Access GitHub repositories, Issues, PRs

---

## Security Considerations

> [!WARNING]
> MCP services have powerful system access capabilities. Ensure:
> - Only enable necessary services
> - Securely store API tokens
> - Limit file system access scope

---

## Related Documentation
- [Quick Start](QUICKSTART.md)
- [Agent Configuration Reference](AGENT_CONFIG.md)
