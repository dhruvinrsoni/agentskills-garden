#!/usr/bin/env python3
"""
Generate documentation from skill schemas.

This tool reads all skill schema.json files and generates:
1. Updated AGENTSKILLS.md with current skill catalog
2. Individual skill README.md files
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_skill_schemas(skills_dir: Path) -> List[Dict[str, Any]]:
    """Load all skill schemas from the skills directory."""
    schemas = []
    for schema_file in skills_dir.rglob("schema.json"):
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
                schema["_path"] = schema_file
                schemas.append(schema)
        except Exception as e:
            print(f"Warning: Failed to load {schema_file}: {e}")
    return schemas


def generate_skill_readme(schema: Dict[str, Any], output_path: Path) -> None:
    """Generate a README.md for a single skill."""
    content = f"""# {schema['name']}

**Skill ID:** `{schema['id']}`  
**Version:** {schema['version']}  
**Level:** {schema['level']} ({get_level_name(schema['level'])})  
**Domain:** {schema['domain']}

## Description

{schema['description']['long']}

## Interface

### Inputs

```json
{json.dumps(schema['interface']['inputs'], indent=2)}
```

### Outputs

```json
{json.dumps(schema['interface']['outputs'], indent=2)}
```

### Context Requirements

{format_context_requirements(schema['interface'].get('context_required', []))}

## Dependencies

{format_dependencies(schema.get('dependencies', []))}

## Validation

{format_validation(schema.get('validation', {}))}

## Usage

### As a Container

```bash
# Build the container
docker build -t agentskills-{schema['id']}:latest .

# Run the skill
docker run -p 8000:8000 agentskills-{schema['id']}:latest

# Execute the skill
curl -X POST http://localhost:8000/execute \\
  -H "Content-Type: application/json" \\
  -d '{{"inputs": {{"example": "value"}}}}'

# Check health
curl http://localhost:8000/health

# Get schema
curl http://localhost:8000/describe
```

### As a Python Module

```python
from skills.{schema['domain']}.{schema['id']} import main

# TODO: Add usage example
```

## Testing

```bash
# Run unit tests
pytest test_main.py -v

# Run with coverage
pytest test_main.py --cov=main --cov-report=html
```

---

*Auto-generated from schema.json by `python tools/generate_docs.py`*
"""
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Generated {output_path}")


def get_level_name(level: int) -> str:
    """Get the human-readable name for a skill level."""
    levels = {
        0: "Primitives",
        1: "Cognitive",
        2: "Task Skills",
        3: "Domain Skills",
        4: "Compound Skills"
    }
    return levels.get(level, "Unknown")


def format_context_requirements(requirements: List[str]) -> str:
    """Format context requirements as a list."""
    if not requirements:
        return "*None*"
    return "\n".join(f"- `{req}`" for req in requirements)


def format_dependencies(dependencies: List[str]) -> str:
    """Format dependencies as a list."""
    if not dependencies:
        return "*None*"
    return "\n".join(f"- `{dep}`" for dep in dependencies)


def format_validation(validation: Dict[str, Any]) -> str:
    """Format validation information."""
    sections = []
    
    if validation.get("test_cases"):
        sections.append(f"**Test Cases:** {len(validation['test_cases'])} defined")
    
    if validation.get("invariants"):
        inv_list = "\n".join(f"- {inv}" for inv in validation['invariants'])
        sections.append(f"**Invariants:**\n{inv_list}")
    
    return "\n\n".join(sections) if sections else "*No validation specifications defined*"


def update_agentskills_catalog(schemas: List[Dict[str, Any]], agentskills_path: Path) -> None:
    """Update the Skill Catalog section in AGENTSKILLS.md."""
    # Group by domain
    by_domain: Dict[str, List[Dict[str, Any]]] = {}
    for schema in schemas:
        domain = schema['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(schema)
    
    # Generate catalog markdown
    catalog_lines = ["## Skill Catalog\n", "<!-- AUTO-GENERATED: Run `python tools/generate_docs.py` to update -->\n"]
    
    for domain, skills in sorted(by_domain.items()):
        # Format domain name
        domain_title = domain.replace("_", " ").title()
        catalog_lines.append(f"\n### Domain: {domain_title}\n")
        catalog_lines.append("\n| Skill ID | Level | Purpose | Status |")
        catalog_lines.append("\n|----------|-------|---------|--------|")
        
        for skill in sorted(skills, key=lambda s: s['id']):
            status = "✅ Active" if skill.get('metadata', {}).get('status') == 'active' else "🚧 Planned"
            catalog_lines.append(
                f"\n| `{skill['id']}` | {skill['level']} | {skill['description']['short']} | {status} |"
            )
    
    catalog_md = "".join(catalog_lines)
    
    # Read current AGENTSKILLS.md
    if not agentskills_path.exists():
        print(f"Warning: {agentskills_path} not found, skipping update")
        return
    
    content = agentskills_path.read_text(encoding="utf-8")
    
    # Find and replace Skill Catalog section
    start_marker = "## Skill Catalog"
    end_marker = "---\n\n## Philosophy"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Warning: Could not find Skill Catalog section markers in AGENTSKILLS.md")
        return
    
    new_content = content[:start_idx] + catalog_md + "\n\n" + content[end_idx:]
    agentskills_path.write_text(new_content, encoding="utf-8")
    print(f"✓ Updated {agentskills_path}")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / "skills"
    agentskills_path = repo_root / "AGENTSKILLS.md"
    
    print("AgentSkills Documentation Generator")
    print("=" * 40)
    
    # Load all schemas
    print(f"\nScanning for skills in {skills_dir}...")
    schemas = load_skill_schemas(skills_dir)
    print(f"Found {len(schemas)} skill(s)")
    
    if not schemas:
        print("\nNo skills found. Create skills with schema.json files first.")
        return
    
    # Generate individual READMEs
    print("\nGenerating skill README files...")
    for schema in schemas:
        skill_dir = schema["_path"].parent
        readme_path = skill_dir / "README.md"
        generate_skill_readme(schema, readme_path)
    
    # Update AGENTSKILLS.md catalog
    print("\nUpdating AGENTSKILLS.md catalog...")
    update_agentskills_catalog(schemas, agentskills_path)
    
    print(f"\n✅ Documentation generation complete!")
    print(f"   Generated {len(schemas)} skill README(s)")
    print(f"   Updated {agentskills_path}")


if __name__ == "__main__":
    main()
