"""
AgentSkills-Garden MCP Server

Exposes all skills as Model Context Protocol (MCP) tools.
Dynamically discovers skills and converts their schemas to MCP tool definitions.

Usage:
    python server.py

Or configure in your MCP client:
    {
      "mcpServers": {
        "agentskills": {
          "command": "python",
          "args": ["path/to/integrations/mcp/server.py"]
        }
      }
    }
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("agentskills-mcp")


# ============================================================================
# Configuration
# ============================================================================


class Config(BaseModel):
    """Server configuration."""
    
    skills_base_url: str = "http://localhost:8000"
    skills_discovery_path: str = None  # If None, use local schema files
    timeout: float = 30.0


def get_config() -> Config:
    """Load configuration from environment or defaults."""
    import os
    return Config(
        skills_base_url=os.environ.get("SKILLS_BASE_URL", "http://localhost:8000"),
        timeout=float(os.environ.get("SKILLS_TIMEOUT", "30")),
    )


# ============================================================================
# Skill Discovery
# ============================================================================


def discover_local_skills() -> list[dict]:
    """Discover skills from local schema files."""
    skills = []
    
    # Find the skills directory relative to this file
    repo_root = Path(__file__).parent.parent.parent
    skills_dir = repo_root / "skills"
    
    if not skills_dir.exists():
        logger.warning(f"Skills directory not found: {skills_dir}")
        return skills
    
    # Find all schema.json files
    for schema_path in skills_dir.rglob("schema.json"):
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            
            # Determine the skill's HTTP port (for multi-service deployments)
            skill_dir = schema_path.parent
            schema["_path"] = str(skill_dir)
            skills.append(schema)
            logger.info(f"Discovered skill: {schema['id']}")
        except Exception as e:
            logger.error(f"Failed to load schema {schema_path}: {e}")
    
    return skills


def schema_to_mcp_tool(skill_schema: dict) -> Tool:
    """Convert an AgentSkills schema to an MCP Tool definition."""
    
    # Extract input schema properties
    interface = skill_schema.get("interface", {})
    input_schema = interface.get("inputs", {"type": "object", "properties": {}})
    
    # Build MCP tool
    tool = Tool(
        name=skill_schema["id"],
        description=skill_schema.get("description", f"Skill: {skill_schema['name']}"),
        inputSchema=input_schema,
    )
    
    return tool


# ============================================================================
# MCP Server Implementation
# ============================================================================


class AgentSkillsMCPServer:
    """MCP Server that exposes AgentSkills as tools."""
    
    def __init__(self):
        self.server = Server("agentskills-garden")
        self.config = get_config()
        self.skills: dict[str, dict] = {}  # skill_id -> schema
        self.http_client = None
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available skills as tools."""
            await self._ensure_skills_loaded()
            
            tools = []
            for skill_id, schema in self.skills.items():
                tool = schema_to_mcp_tool(schema)
                tools.append(tool)
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a skill."""
            await self._ensure_skills_loaded()
            
            if name not in self.skills:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown skill '{name}'. Available: {list(self.skills.keys())}"
                )]
            
            try:
                result = await self._execute_skill(name, arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error executing skill {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing skill: {str(e)}"
                )]
    
    async def _ensure_skills_loaded(self):
        """Ensure skills are discovered and loaded."""
        if not self.skills:
            local_skills = discover_local_skills()
            for schema in local_skills:
                self.skills[schema["id"]] = schema
            logger.info(f"Loaded {len(self.skills)} skills")
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=self.config.timeout)
        return self.http_client
    
    async def _execute_skill(self, skill_id: str, inputs: dict) -> dict:
        """Execute a skill via HTTP or direct import."""
        schema = self.skills[skill_id]
        
        # Try HTTP execution first (for running skill containers)
        try:
            client = await self._get_http_client()
            
            # Determine endpoint URL
            # In a multi-service deployment, each skill runs on its own port
            # For single-service, all skills share the base URL
            base_url = self.config.skills_base_url
            
            response = await client.post(
                f"{base_url}/execute",
                json={"inputs": inputs},
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.ConnectError:
            # Fall back to direct Python execution
            logger.info(f"HTTP failed for {skill_id}, trying direct execution")
            return await self._execute_skill_direct(skill_id, inputs)
    
    async def _execute_skill_direct(self, skill_id: str, inputs: dict) -> dict:
        """Execute a skill by importing its Python module directly."""
        schema = self.skills[skill_id]
        skill_path = Path(schema.get("_path", ""))
        
        if not skill_path.exists():
            raise ValueError(f"Skill path not found: {skill_path}")
        
        # Add skill directory to path and import
        import importlib.util
        
        main_py = skill_path / "main.py"
        if not main_py.exists():
            raise ValueError(f"main.py not found for skill: {skill_id}")
        
        spec = importlib.util.spec_from_file_location(f"skill_{skill_id}", main_py)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the main execution function
        # Convention: function named after skill_id or "execute"
        func_name = skill_id
        if not hasattr(module, func_name):
            func_name = "execute"
        if not hasattr(module, func_name):
            # Try to find a function that takes inputs
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and not name.startswith("_"):
                    func_name = name
                    break
        
        func = getattr(module, func_name, None)
        if func is None:
            raise ValueError(f"No executable function found in {skill_id}")
        
        # Execute
        result = func(inputs)
        
        # Handle async functions
        if asyncio.iscoroutine(result):
            result = await result
        
        return {"status": "success", "outputs": result}
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def cleanup(self):
        """Clean up resources."""
        if self.http_client:
            await self.http_client.aclose()


# ============================================================================
# Entry Point
# ============================================================================


async def main():
    """Main entry point."""
    server = AgentSkillsMCPServer()
    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
