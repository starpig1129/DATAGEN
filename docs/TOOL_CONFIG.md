# Tool Configuration Guide

This document explains how to configure tools for agents.

## Overview

Tools are capabilities that allow agents to interact with the external world. All tools are centrally managed by the `ToolFactory`.

---

## Available Tools

### Core Tools

| Tool Name | Description | Use Case |
|-----------|-------------|----------|
| `execute_code` | Execute Python code | Data processing, analysis |
| `execute_command` | Execute Shell commands | System operations |
| `list_directory` | List directory contents | File exploration |

### File Operation Tools

| Tool Name | Description | Use Case |
|-----------|-------------|----------|
| `read_document` | Read file contents | Read data, reports |
| `create_document` | Create new files | Generate reports |
| `edit_document` | Edit existing files | Modify content |
| `collect_data` | Collect data | Data aggregation |

### Research Tools

| Tool Name | Description | Use Case |
|-----------|-------------|----------|
| `wikipedia` | Query Wikipedia | Background knowledge |
| `arxiv` | Query arXiv papers | Academic research |
| `google_search` | Google search | Web information |
| `scrape_webpages` | Web scraping | Web content extraction |

### System Tools

| Tool Name | Description | Use Case |
|-----------|-------------|----------|
| `lookup_skill` | Query skill content | Auto-added if skills configured |

---

## Configuration

### Specify in config.yaml

```yaml
tools:
  - execute_code
  - read_document
  - wikipedia
```

### Configuration Examples

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

## Custom Tools

### Adding New Tools to ToolFactory

1. Create the tool function in `src/tools/`
2. Register it in `src/tools/factory.py`:

```python
from .my_tools import my_custom_tool

class ToolFactory:
    _registry = {
        # ... existing tools ...
        "my_custom_tool": my_custom_tool,
    }
```

3. Reference it in the agent's `config.yaml`:
```yaml
tools:
  - my_custom_tool
```

---

## Fallback Mechanism

If `tools` is not defined in `config.yaml`, the system falls back to the agent class's `_get_tools()` method.

---

## Related Documentation
- [Quick Start](QUICKSTART.md)
- [Agent Configuration Reference](AGENT_CONFIG.md)
