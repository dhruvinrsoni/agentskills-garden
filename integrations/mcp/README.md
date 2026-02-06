# AgentSkills MCP Integration

This directory contains the Model Context Protocol (MCP) server that exposes AgentSkills-Garden skills as MCP tools.

## Overview

The MCP server automatically discovers all skills in the repository and exposes them as tools that can be used by MCP-compatible clients (Claude Desktop, VS Code with Copilot, etc.).

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your MCP Client

Add to your MCP client configuration (e.g., Claude Desktop's `config.json`):

```json
{
  "mcpServers": {
    "agentskills": {
      "command": "python",
      "args": ["path/to/agentskills-garden/integrations/mcp/server.py"],
      "env": {
        "SKILLS_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 3. Start Skill Services (Optional)

If you want skills to run as HTTP services:

```bash
cd skills/01_code_understanding/summarize_code
uvicorn main:app --port 8001
```

Or use Docker Compose:

```bash
docker-compose -f infra/docker-compose.yml up
```

If no HTTP service is running, the MCP server will execute skills directly via Python import.

## How It Works

1. **Discovery**: The server scans `skills/*/*/schema.json` to find all available skills
2. **Schema Conversion**: Each skill's JSON Schema is converted to an MCP tool definition
3. **Execution**: When a tool is called:
   - First tries HTTP execution (if skill service is running)
   - Falls back to direct Python module execution

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILLS_BASE_URL` | `http://localhost:8000` | Base URL for skill HTTP services |
| `SKILLS_TIMEOUT` | `30` | HTTP request timeout in seconds |

## Available Tools

Once connected, the following skills are available as MCP tools:

### Code Understanding Domain
- `summarize_code` - Summarize file/function with context
- `analyze_history` - Explain why code exists via git history
- `map_dependencies` - Trace imports/dependencies for a module
- `detect_smells` - Identify code smells and survivor patterns

### Translate Needs Domain
- `clarify_requirement` - Ask probing questions on vague requirements
- `analyze_tradeoffs` - Surface hidden tradeoffs in requests
- `translate_stakeholder` - Convert business-speak to technical spec

## Example Usage

Once configured, you can use skills in your MCP client:

```
User: Use summarize_code to analyze main.py

[MCP calls summarize_code with {"file_path": "main.py"}]