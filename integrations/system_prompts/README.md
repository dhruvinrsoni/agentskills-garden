# AgentSkills System Prompts

Composable prompt templates that encode AgentSkills behaviors into AI system prompts.

## Overview

While tools provide **actions** and RAG provides **knowledge**, system prompts define **behavior**. This directory contains prompt templates that help AI models reason like experienced engineers when facing the 7 capability gaps.

## Prompt Structure

Each prompt template follows a consistent structure:
- **Role Definition**: Who the AI should emulate
- **Principles**: Core reasoning principles
- **Behaviors**: Specific behaviors to exhibit
- **Guardrails**: What to avoid
- **Examples**: Demonstration of expected reasoning

## Available Prompts

### Core Prompts

| Prompt | Gap Addressed | Purpose |
|--------|---------------|---------|
| `legacy_code_whisperer.md` | #3 Legacy Code | Approach old code with curiosity, not judgment |
| `business_translator.md` | #4 Business Needs | Bridge stakeholder language to technical specs |
| `survivor_pattern_detective.md` | #3 Legacy Code | Find intentional workarounds in messy code |
| `tradeoff_advisor.md` | #4 Business Needs | Surface hidden costs and consequences |

### Compound Prompts

| Prompt | Combines | Purpose |
|--------|----------|---------|
| `senior_engineer.md` | All core prompts | Full senior engineer reasoning patterns |
| `code_archaeologist.md` | Legacy + Survivor | Deep dive into historical code decisions |

## Usage

### Direct Inclusion

```python
with open("prompts/legacy_code_whisperer.md") as f:
    system_prompt = f.read()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Why does this code exist?"}
    ]
)
```

### Composition

```python
from compose import compose_prompts

system_prompt = compose_prompts([
    "legacy_code_whisperer",
    "survivor_pattern_detective",
])
```

### With Tools

```python
system_prompt = compose_prompts(["senior_engineer"])
tools = load_tools(["summarize_code", "analyze_history"])

response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    system=system_prompt,
    tools=tools,
)
```

## Prompt Design Philosophy

### 1. Encode Experience, Not Rules

❌ "Always check for null values"
✅ "Before refactoring, ask: why might this null check exist? What edge case did someone encounter?"

### 2. Encourage Questions Over Answers

❌ "This code is inefficient and should use a HashMap"
✅ "This appears inefficient. Before changing, consider: Is there a reason a list was chosen? Check git blame for context."

### 3. Model Uncertainty

❌ "The best solution is..."
✅ "Based on the constraints I can see, one option is... However, I'd want to verify..."

### 4. Preserve Intent

❌ "Clean up this messy function"
✅ "This function has grown complex. Before simplifying, let's understand what each branch handles and whether those cases still exist."
