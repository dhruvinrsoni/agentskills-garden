# AgentSkills Garden 🌱

> *A composable library of AI agent skills designed to bridge the gaps AI cannot replicate.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/dhruvinrsoni/agentskills-garden/workflows/CI/badge.svg)](https://github.com/dhruvinrsoni/agentskills-garden/actions)

AI has automated 80% of coding, but critical capabilities remain out of reach. AgentSkills Garden provides specialized skills that enable any AI model to excel at:

🏗️ **Architectural reasoning** | 🐛 **Debugging distributed systems** | 📚 **Understanding legacy code**  
💼 **Translating business needs** | 🎯 **Strategic systems thinking** | ⚖️ **Legal/ethical accountability** | 🤝 **Human connection**

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dhruvinrsoni/agentskills-garden.git
cd agentskills-garden

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest skills/ --cov

# Generate documentation
python tools/generate_docs.py
```

## What's Inside

- **📦 Skill Library**: Composable, containerized microservices with standardized HTTP APIs
- **📋 JSON Schemas**: Portable skill definitions that work across any AI model
- **🧪 Three-Tiered Testing**: Unit tests, LLM-as-judge evals, and human review
- **🐳 Docker Support**: Each skill runs as an isolated, cloud-native container
- **🔌 Multi-Platform**: Integrations for MCP, OpenAI Functions, and custom prompts

## Project Structure

```
agentskills-garden/
├── skills/                  # Skill implementations
│   ├── 01_code_understanding/
│   └── 02_translate_needs/
├── schemas/                 # JSON Schema definitions
├── infra/                   # Docker and infrastructure
├── evals/                   # Evaluation framework
├── tools/                   # Build and automation tools
└── AGENTSKILLS.md          # Full documentation
```

## Current Status

🚧 **Phase 0: Repository Scaffolding** ✅ COMPLETE  
🔄 **Phase 1: Skill Contract Definition** - In Progress  
📋 **Phase 2: Code Understanding Skills** - Planned

See [AGENTSKILLS.md](AGENTSKILLS.md) for the complete roadmap.

## Contributing

We welcome contributions! Please read:

1. [AGENTSKILLS.md](AGENTSKILLS.md) - Project philosophy and architecture
2. [CLA.md](.github/CLA.md) - Contributor License Agreement
3. [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines

## Philosophy

> *"The code is being automated. The engineering is not."*

AgentSkills Garden focuses on the irreplaceable aspects of software engineering—the tacit knowledge, contextual judgment, and human insight that makes the difference between code that works and systems that endure.

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

**Remember:** Goal → Context → Source → Expectations *(G)iraffe (C)an (S)ee (E)verything* 🦒
