# Contributing to AgentSkills Garden

Thank you for your interest in contributing! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Skill Development Guide](#skill-development-guide)
5. [Testing Requirements](#testing-requirements)
6. [Commit Conventions](#commit-conventions)
7. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

Be respectful, constructive, and collaborative. We're building something that helps everyone.

---

## Getting Started

### Prerequisites

- Python 3.11 or 3.12
- Docker (for containerization)
- Git
- A GitHub account

### Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/agentskills-garden.git
cd agentskills-garden

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Verify setup
pytest skills/ --cov
python tools/generate_docs.py
```

---

## Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-skill-name
   ```

2. **Make your changes** (see Skill Development Guide below)

3. **Run tests locally**:
   ```bash
   # Format code
   black .
   
   # Lint
   ruff check .
   
   # Type check
   mypy skills/ tools/ evals/
   
   # Unit tests
   pytest skills/ --cov
   
   # Validate schemas
   python -m jsonschema --instance skills/your_skill/schema.json schemas/skill.schema.json
   ```

4. **Commit using Conventional Commits** (see below)

5. **Push and create a Pull Request**

---

## Skill Development Guide

### Step 1: Plan Your Skill

Before coding, answer:
- Which of the 7 gaps does this address?
- What level (0-4) is this skill?
- What domain does it belong to?
- What are the inputs and outputs?

### Step 2: Create Skill Directory

```bash
# Example for a Level 1 skill in code_understanding domain
mkdir -p skills/01_code_understanding/your_skill_name
cd skills/01_code_understanding/your_skill_name
```

### Step 3: Define the Schema

Create `schema.json`:

```json
{
  "id": "your_skill_name",
  "name": "Your Skill Display Name",
  "version": "0.1.0",
  "level": 1,
  "domain": "code_understanding",
  "description": {
    "short": "Brief description for LLM tool selection",
    "long": "Detailed explanation of what this skill does and why it's useful."
  },
  "interface": {
    "inputs": {
      "type": "object",
      "properties": {
        "your_param": {
          "type": "string",
          "description": "Description of parameter"
        }
      },
      "required": ["your_param"]
    },
    "outputs": {
      "type": "object",
      "properties": {
        "result": {
          "type": "string",
          "description": "Description of output"
        }
      },
      "required": ["result"]
    },
    "context_required": ["filesystem_read"]
  },
  "dependencies": [],
  "validation": {
    "test_cases": [
      {
        "name": "basic_case",
        "input": {"your_param": "test"},
        "expected_output": {"result": "expected"}
      }
    ],
    "invariants": [
      "Output must be valid JSON",
      "Execution time < 5 seconds"
    ]
  }
}
```

### Step 4: Implement the Skill

Create `main.py`:

```python
"""
Your Skill Name

Description of what this skill does.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
from pathlib import Path

# Load schema
SCHEMA_PATH = Path(__file__).parent / "schema.json"
with open(SCHEMA_PATH) as f:
    SKILL_SCHEMA = json.load(f)

app = FastAPI(
    title=SKILL_SCHEMA["name"],
    description=SKILL_SCHEMA["description"]["long"],
    version=SKILL_SCHEMA["version"]
)


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint."""
    inputs: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ExecuteResponse(BaseModel):
    """Response model for successful execution."""
    status: str = "success"
    outputs: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute the skill with provided inputs."""
    try:
        # Validate inputs match schema
        # TODO: Add proper validation
        
        # Implement skill logic here
        result = process_skill_logic(request.inputs)
        
        return ExecuteResponse(
            outputs=result,
            metadata={"execution_time_ms": 0}  # TODO: Track actual time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": SKILL_SCHEMA["version"]
    }


@app.get("/describe")
async def describe():
    """Return the skill's schema."""
    return SKILL_SCHEMA


def process_skill_logic(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core skill logic implementation.
    
    Args:
        inputs: Input parameters matching the skill's input schema
        
    Returns:
        Output data matching the skill's output schema
    """
    # TODO: Implement your skill logic here
    return {"result": "placeholder"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 5: Write Tests

Create `test_main.py`:

```python
"""Tests for your_skill_name skill."""

import pytest
from fastapi.testclient import TestClient
from main import app, process_skill_logic

client = TestClient(app)


def test_health_endpoint():
    """Test health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_describe_endpoint():
    """Test schema retrieval."""
    response = client.get("/describe")
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["id"] == "your_skill_name"


def test_execute_basic():
    """Test basic execution."""
    response = client.post(
        "/execute",
        json={"inputs": {"your_param": "test"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "outputs" in data


def test_skill_logic():
    """Test core skill logic."""
    result = process_skill_logic({"your_param": "test"})
    assert "result" in result
    assert isinstance(result["result"], str)


# Add more tests for edge cases, errors, etc.
```

### Step 6: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy skill files
COPY schema.json main.py ./
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run the skill
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `requirements.txt`:

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
```

### Step 7: Generate Documentation

```bash
# Auto-generate README.md from schema
python tools/generate_docs.py
```

---

## Testing Requirements

All skills must have:

1. **Unit tests** with >80% coverage
2. **Schema validation** (automatically checked by CI)
3. **Test cases defined in schema.json**
4. **Docker build success**

Run all checks:

```bash
pytest skills/your_domain/your_skill/ --cov --cov-report=html
docker build -t test-skill skills/your_domain/your_skill/
```

---

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New skill or feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### Scopes

Use the skill's `snake_case` ID as scope, or:
- `infra`: Infrastructure changes
- `ci`: CI/CD changes
- `evals`: Evaluation framework changes
- `tools`: Build tools changes

### Examples

```bash
git commit -m "feat(summarize_code): add support for TypeScript files"
git commit -m "fix(analyze_history): handle repositories without initial commit"
git commit -m "docs(clarify_requirement): add examples for stakeholder translation"
git commit -m "test(map_dependencies): add fixture for circular imports"
```

---

## Pull Request Process

1. **Sign the CLA**: On your first contribution, include this in your PR description:
   ```
   I agree to the terms of the Contributor License Agreement (CLA) as outlined in .github/CLA.md
   ```

2. **PR Title**: Use Conventional Commit format

3. **PR Description**: Include:
   - What changed and why
   - Which gap(s) this addresses
   - Testing performed
   - Screenshots/examples if applicable

4. **CI Checks**: Ensure all checks pass:
   - ✅ Linting (Black, Ruff, MyPy)
   - ✅ Tests (pytest)
   - ✅ Schema validation
   - ✅ Docker build

5. **Review**: Address feedback promptly and professionally

6. **Merge**: Once approved, a maintainer will merge your PR

---

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security issues**: Email the maintainer directly

---

Thank you for contributing to AgentSkills Garden! 🌱
