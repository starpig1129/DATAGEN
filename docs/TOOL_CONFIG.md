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

## Security & Resource Limits

### Configuration File

Tool limits are configured in `config/tool_limits.yaml`:

```yaml
# Execution limits
execution:
  timeout_seconds: 60              # Fixed timeout (null = no limit)
  max_memory_mb: 512               # Memory limit (Linux only)
  max_output_chars: 50000          # Truncate output
  progress_timeout_seconds: 300    # For ML/DL tasks

# File operation limits  
file_operations:
  max_read_bytes: 5242880          # 5MB
  max_read_lines: 10000
  max_write_bytes: 10485760        # 10MB
  allowed_extensions: [.py, .md, .txt, .csv, .json]
  blocked_paths: [/etc, /sys, ~/.ssh]

# Global switches
enable_security_scan: true
enable_write_validation: true
```

### execute_code Parameters

```python
execute_code(
    input_code="...",
    codefile_name="code.py",
    timeout=60,              # Fixed timeout in seconds
    memory_mb=512,           # Memory limit (Linux)
    progress_timeout=300     # Timeout only if no output
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | `int \| None` | Kill after N seconds |
| `memory_mb` | `int \| None` | Memory limit in MB (Linux only) |
| `progress_timeout` | `int \| None` | Timeout only if no stdout for N seconds |

> **Tip**: For ML/DL training, use `progress_timeout` instead of `timeout` to allow long-running tasks that print progress.

### Security Features

| Feature | Description |
|---------|-------------|
| **Code Scanning** | AST analysis blocks dangerous patterns (`eval`, `os.system`, etc.) |
| **Path Validation** | Blocks access to sensitive paths (`/etc`, `~/.ssh`) |
| **Content Validation** | Warns on incomplete markers (TODO, FIXME) |
| **Size Limits** | Prevents reading/writing excessively large files |

### Blocked Patterns (Default)

```
os.system, subprocess.call, subprocess.run, subprocess.Popen,
shutil.rmtree, eval(, exec(, __import__
```

---

## Agent Configuration

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

## Programmatic Access

```python
from src.tools.factory import ToolFactory

# Get current configuration
config = ToolFactory.get_config()

# Get limits only
limits = ToolFactory.get_limits()
print(limits["execution"]["timeout_seconds"])
```

---

## Fallback Mechanism

If `tools` is not defined in `config.yaml`, the system falls back to the agent class's `_get_tools()` method.

---

## Related Documentation
- [Quick Start](QUICKSTART.md)
- [Agent Configuration Reference](AGENT_CONFIG.md)

