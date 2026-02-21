Local quick-start — minimal setup

Goal: run a local, minimal skill runner that uses the `skills` registry and returns a demo output (no heavy model required).

Prereqs
- Python 3.8+
- (optional) A local model HTTP endpoint (TGI, vLLM, or similar). If you don't have one, the runner returns a demo response.

Install

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run the interactive CLI (demo mode):

```bash
python scripts/cli.py
```

If you have a local model endpoint (JSON API), run:

```bash
python scripts/cli.py --model-endpoint http://localhost:8080/generate
```

What it does
- Loads `registry.yaml` and skill markdown files.
- Uses a tiny librarian (difflib-based) to pick the best skill for your query.
- Builds a prompt from the skill content + user intent.
- If `--model-endpoint` is provided, POSTs JSON {"prompt":...,"max_tokens":512} and prints the response.
- Otherwise prints a demo placeholder output.

Next steps (if this looks good)
- Hook a real local model (TGI/vLLM) to `--model-endpoint`.
- Replace the naive librarian with semantic embeddings for better skill routing.
- Wire `scratchpad` and `auditor` skill protocols into the orchestration loop.
