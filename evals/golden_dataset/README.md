# Golden Dataset for Skill Evaluations

This directory contains curated test cases for evaluating skills using the LLM-as-judge methodology.

## Structure

Each skill has its own JSON file: `{skill_id}.json`

```
golden_dataset/
├── summarize_code.json
├── analyze_history.json
├── map_dependencies.json
└── ...
```

## Format

Each file contains an array of test cases:

```json
[
  {
    "name": "Test case name",
    "description": "What this test validates",
    "input": {
      "param1": "value1",
      "param2": "value2"
    },
    "expected_output": {
      "result": "expected value",
      "metadata": {"key": "value"}
    },
    "tags": ["edge-case", "performance"],
    "acceptance_criteria": [
      "Output must include X",
      "Response time < 5s"
    ]
  }
]
```

## Creating Test Cases

1. **Typical Use Cases**: Cover the most common usage patterns
2. **Edge Cases**: Boundary conditions, empty inputs, extreme values
3. **Error Scenarios**: Invalid inputs that should fail gracefully
4. **Performance Cases**: Inputs that test efficiency

## Example

See example files in this directory once skills are implemented.

## Usage

```bash
# Run evaluations against golden dataset
python evals/judge.py --dataset evals/golden_dataset/ --skill summarize_code

# Run all skills
python evals/judge.py --dataset evals/golden_dataset/ --all
```
