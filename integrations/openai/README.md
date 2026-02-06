# AgentSkills OpenAI Integration

Generate OpenAI function/tool definitions from AgentSkills-Garden skill schemas.

## Overview

This integration converts skill schemas to OpenAI's function calling format, enabling you to use AgentSkills as tools in OpenAI API calls (GPT-4, GPT-4 Turbo, etc.).

## Quick Start

### Generate Tool Definitions

```bash
# Generate tools.json with all skills
python generate.py --output tools.json

# Generate for specific skill
python generate.py --skill summarize_code --output summarize_code.json

# Generate legacy functions format
python generate.py --format functions --output functions.json
```

### Generate Client Code

```bash
# Python client
python generate.py --client python --output agentskills_openai.py

# TypeScript client
python generate.py --client typescript --output agentskills-openai.ts
```

## Usage with OpenAI API

### Python

```python
from openai import OpenAI
import json

# Load generated definitions
with open("tools.json") as f:
    tools = json.load(f)

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Summarize main.py"}],
    tools=tools,
    tool_choice="auto",
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        skill_id = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        # Execute skill via HTTP
        import httpx
        result = httpx.post(
            "http://localhost:8000/execute",
            json={"inputs": args}
        ).json()
        
        print(f"Skill {skill_id} result:", result)
```

### TypeScript

```typescript
import OpenAI from 'openai';
import tools from './tools.json';

const client = new OpenAI();

const response = await client.chat.completions.create({
  model: 'gpt-4-turbo-preview',
  messages: [{ role: 'user', content: 'Summarize main.py' }],
  tools,
  tool_choice: 'auto',
});

// Handle tool calls...
```

## Generated Format

### Tools Format (Recommended)

```json
[
  {
    "type": "function",
    "function": {
      "name": "summarize_code",
      "description": "Summarize file/function with context",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the file to summarize"
          }
        },
        "required": ["file_path"]
      }
    }
  }
]
```

### Functions Format (Legacy)

```json
[
  {
    "name": "summarize_code",
    "description": "Summarize file/function with context",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "Path to the file to summarize"
        }
      },
      "required": ["file_path"]
    }
  }
]
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `summarize_code` | Summarize file/function with context |
| `analyze_history` | Explain why code exists via git history |
| `map_dependencies` | Trace imports/dependencies for a module |
| `detect_smells` | Identify code smells and survivor patterns |
| `clarify_requirement` | Ask probing questions on vague requirements |
| `analyze_tradeoffs` | Surface hidden tradeoffs in requests |
| `translate_stakeholder` | Convert business-speak to technical spec |
