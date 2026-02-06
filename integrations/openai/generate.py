"""
OpenAI Function Definitions Generator

Converts AgentSkills-Garden skill schemas to OpenAI function calling format.
Supports both the legacy "functions" format and the newer "tools" format.

Usage:
    # Generate function definitions
    python generate.py --output functions.json
    
    # Generate tool definitions (recommended)
    python generate.py --format tools --output tools.json
    
    # Generate for specific skill
    python generate.py --skill summarize_code
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal


def find_skills_directory() -> Path:
    """Find the skills directory relative to this file."""
    repo_root = Path(__file__).parent.parent.parent
    skills_dir = repo_root / "skills"
    
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")
    
    return skills_dir


def discover_skills(skills_dir: Path, skill_filter: str = None) -> list[dict]:
    """Discover all skill schemas."""
    skills = []
    
    for schema_path in skills_dir.rglob("schema.json"):
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            
            if skill_filter and schema["id"] != skill_filter:
                continue
            
            skills.append(schema)
        except Exception as e:
            print(f"Warning: Failed to load {schema_path}: {e}", file=sys.stderr)
    
    return skills


def schema_to_openai_function(skill_schema: dict) -> dict:
    """Convert skill schema to OpenAI function format (legacy)."""
    interface = skill_schema.get("interface", {})
    input_schema = interface.get("inputs", {"type": "object", "properties": {}})
    
    # Clean up the input schema for OpenAI
    clean_schema = {
        "type": "object",
        "properties": input_schema.get("properties", {}),
    }
    
    if "required" in input_schema:
        clean_schema["required"] = input_schema["required"]
    
    return {
        "name": skill_schema["id"],
        "description": skill_schema.get("description", f"Execute the {skill_schema['name']} skill"),
        "parameters": clean_schema,
    }


def schema_to_openai_tool(skill_schema: dict) -> dict:
    """Convert skill schema to OpenAI tools format (recommended)."""
    function_def = schema_to_openai_function(skill_schema)
    
    return {
        "type": "function",
        "function": function_def,
    }


def generate_definitions(
    output_format: Literal["functions", "tools"] = "tools",
    skill_filter: str = None,
) -> list[dict]:
    """Generate OpenAI definitions for all skills."""
    skills_dir = find_skills_directory()
    skills = discover_skills(skills_dir, skill_filter)
    
    if output_format == "tools":
        return [schema_to_openai_tool(s) for s in skills]
    else:
        return [schema_to_openai_function(s) for s in skills]


def generate_client_code(skills: list[dict], language: str = "python") -> str:
    """Generate client code for using the skills with OpenAI."""
    if language == "python":
        return _generate_python_client(skills)
    elif language == "typescript":
        return _generate_typescript_client(skills)
    else:
        raise ValueError(f"Unsupported language: {language}")


def _generate_python_client(skills: list[dict]) -> str:
    """Generate Python client code."""
    skill_names = [s.get("function", s).get("name", s.get("name")) for s in skills]
    
    code = '''"""
Auto-generated OpenAI client for AgentSkills-Garden.

Usage:
    from agentskills_openai import create_agent, run_skill
    
    # Create an agent with all skills
    agent = create_agent()
    
    # Or run a specific skill
    result = run_skill("summarize_code", {"file_path": "main.py"})
"""

import json
import httpx
from openai import OpenAI

# Base URL for skill services
SKILLS_BASE_URL = "http://localhost:8000"

# Available skill definitions
TOOLS = '''
    
    code += json.dumps(skills, indent=2)
    
    code += '''

def create_client() -> OpenAI:
    """Create an OpenAI client."""
    return OpenAI()


def create_agent(model: str = "gpt-4-turbo-preview") -> dict:
    """Create agent configuration with all skills as tools."""
    return {
        "model": model,
        "tools": TOOLS,
        "tool_choice": "auto",
    }


def run_skill(skill_id: str, inputs: dict, base_url: str = SKILLS_BASE_URL) -> dict:
    """Execute a skill via HTTP."""
    response = httpx.post(
        f"{base_url}/execute",
        json={"inputs": inputs},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def handle_tool_call(tool_call) -> str:
    """Handle a tool call from OpenAI."""
    skill_id = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    result = run_skill(skill_id, arguments)
    return json.dumps(result)


def run_conversation(messages: list[dict], model: str = "gpt-4-turbo-preview") -> str:
    """Run a conversation with tool use."""
    client = create_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    
    message = response.choices[0].message
    
    # Handle tool calls if present
    if message.tool_calls:
        messages.append(message)
        
        for tool_call in message.tool_calls:
            result = handle_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        
        # Get final response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
    
    return message.content


if __name__ == "__main__":
    # Example usage
    result = run_conversation([
        {"role": "user", "content": "Summarize the main.py file"}
    ])
    print(result)
'''
    
    return code


def _generate_typescript_client(skills: list[dict]) -> str:
    """Generate TypeScript client code."""
    code = '''/**
 * Auto-generated OpenAI client for AgentSkills-Garden.
 * 
 * Usage:
 *   import { createAgent, runSkill, TOOLS } from './agentskills-openai';
 */

import OpenAI from 'openai';

// Base URL for skill services
const SKILLS_BASE_URL = process.env.SKILLS_BASE_URL || 'http://localhost:8000';

// Available skill definitions
export const TOOLS: OpenAI.Chat.Completions.ChatCompletionTool[] = '''
    
    code += json.dumps(skills, indent=2)
    
    code += ''';

export function createClient(): OpenAI {
  return new OpenAI();
}

export async function runSkill(skillId: string, inputs: Record<string, any>): Promise<any> {
  const response = await fetch(`${SKILLS_BASE_URL}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ inputs }),
  });
  
  if (!response.ok) {
    throw new Error(`Skill execution failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function handleToolCall(toolCall: OpenAI.Chat.Completions.ChatCompletionMessageToolCall): Promise<string> {
  const skillId = toolCall.function.name;
  const args = JSON.parse(toolCall.function.arguments);
  
  const result = await runSkill(skillId, args);
  return JSON.stringify(result);
}
'''
    
    return code


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate OpenAI function definitions")
    parser.add_argument(
        "--format",
        choices=["functions", "tools"],
        default="tools",
        help="Output format (default: tools)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--skill",
        help="Generate for specific skill only",
    )
    parser.add_argument(
        "--client",
        choices=["python", "typescript"],
        help="Generate client code in specified language",
    )
    
    args = parser.parse_args()
    
    definitions = generate_definitions(args.format, args.skill)
    
    if args.client:
        output = generate_client_code(definitions, args.client)
    else:
        output = json.dumps(definitions, indent=2)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Generated {len(definitions)} definitions to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
