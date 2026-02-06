"""
Prompt Composition Utility

Combines multiple system prompts into a cohesive whole.

Usage:
    from compose import compose_prompts
    
    # Compose multiple prompts
    system_prompt = compose_prompts([
        "legacy_code_whisperer",
        "survivor_pattern_detective",
    ])
    
    # Or load a single prompt
    prompt = load_prompt("business_translator")
"""

from pathlib import Path
from typing import Union


def get_prompts_directory() -> Path:
    """Get the prompts directory."""
    return Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a single prompt by name."""
    prompts_dir = get_prompts_directory()
    
    # Try with .md extension
    prompt_path = prompts_dir / f"{name}.md"
    if not prompt_path.exists():
        prompt_path = prompts_dir / name
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {name}")
    
    with open(prompt_path) as f:
        return f.read()


def compose_prompts(
    names: list[str],
    separator: str = "\n\n---\n\n",
    include_header: bool = True,
) -> str:
    """
    Compose multiple prompts into one.
    
    Args:
        names: List of prompt names to compose
        separator: String to use between prompts
        include_header: Whether to include a composition header
    
    Returns:
        Combined prompt string
    """
    prompts = []
    
    if include_header:
        prompts.append(f"""# Composed System Prompt

This prompt combines the following modules:
{chr(10).join(f'- {name}' for name in names)}

Each module provides complementary reasoning patterns that work together.

---
""")
    
    for name in names:
        prompt = load_prompt(name)
        prompts.append(prompt)
    
    return separator.join(prompts)


def list_available_prompts() -> list[str]:
    """List all available prompts."""
    prompts_dir = get_prompts_directory()
    
    if not prompts_dir.exists():
        return []
    
    return [
        p.stem for p in prompts_dir.glob("*.md")
        if not p.name.startswith("_")
    ]


def create_role_prompt(
    role: str,
    prompts: list[str],
    additional_context: str = "",
) -> str:
    """
    Create a role-specific prompt combining multiple modules.
    
    Args:
        role: The role name (e.g., "Senior Software Engineer")
        prompts: List of prompt modules to include
        additional_context: Additional context to prepend
    
    Returns:
        Complete role prompt
    """
    header = f"""# {role}

You are an AI assistant acting as a {role}. You combine expertise from multiple domains to provide comprehensive guidance.

{additional_context}

---

"""
    
    composed = compose_prompts(prompts, include_header=False)
    
    return header + composed


# Predefined role compositions
ROLE_COMPOSITIONS = {
    "senior_engineer": [
        "legacy_code_whisperer",
        "business_translator",
        "survivor_pattern_detective",
        "tradeoff_advisor",
    ],
    "code_archaeologist": [
        "legacy_code_whisperer",
        "survivor_pattern_detective",
    ],
    "tech_lead": [
        "business_translator",
        "tradeoff_advisor",
    ],
}


def get_role_prompt(role: str) -> str:
    """Get a predefined role prompt."""
    if role not in ROLE_COMPOSITIONS:
        raise ValueError(
            f"Unknown role: {role}. Available: {list(ROLE_COMPOSITIONS.keys())}"
        )
    
    prompts = ROLE_COMPOSITIONS[role]
    return create_role_prompt(role.replace("_", " ").title(), prompts)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compose system prompts")
    parser.add_argument(
        "prompts",
        nargs="*",
        help="Prompt names to compose (or use --role)",
    )
    parser.add_argument(
        "--role",
        choices=list(ROLE_COMPOSITIONS.keys()),
        help="Use a predefined role composition",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available prompts",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)",
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available prompts:")
        for prompt in list_available_prompts():
            print(f"  - {prompt}")
        print("\nPredefined roles:")
        for role, prompts in ROLE_COMPOSITIONS.items():
            print(f"  - {role}: {', '.join(prompts)}")
    elif args.role:
        result = get_role_prompt(args.role)
        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
        else:
            print(result)
    elif args.prompts:
        result = compose_prompts(args.prompts)
        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
        else:
            print(result)
    else:
        parser.print_help()
