# Dopamine Coach - Gemini Provider README

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Run Example

```bash
python example_usage.py
```

## Project Structure

- `decomposition_agent.py` - Core Gemini decomposition agent logic
- `config.py` - Gemini API configuration and settings
- `system_prompt.py` - AI Constitution and output specification
- `utils.py` - JSON validation and formatting utilities
- `example_usage.py` - Usage examples and demonstrations

## Configuration

All settings are managed in `config.py`:

- `API_PROVIDER`: Set to "gemini"
- `MODEL_ID`: Gemini model ("gemini-2.5-flash")
- `API_BASE_URL`: Gemini endpoint ("https://generativelanguage.googleapis.com/v1beta/openai/")
- `API_KEY`: Read from GEMINI_API_KEY environment variable
- `TEMPERATURE`: Creativity level (0.7 for balanced)
- `MAX_TOKENS`: Maximum response length (2000)

## Usage

### Basic Decomposition

```python
from decomposition_agent import DecompositionAgent

agent = DecompositionAgent()
result = agent.decompose("I need to refactor my authentication system")
print(result.to_json())
```

### Batch Processing

```python
user_inputs = [
    "Set up CI/CD pipeline",
    "Implement rate limiting",
    "Migrate database"
]
results = agent.batch_decompose(user_inputs)
```

### Validation

```python
is_valid, errors = result.validate_all()
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

## Output Format

All outputs are JSON-only (no markdown or UI formatting):

```json
{
  "task": {
    "task_id": "1",
    "task_title": "Refactor authentication system",
    "task_priority": "High",
    "intent_priority": "High",
    "estimated_total_session_time": 48,
    "total_steps": 3,
    "steps": [
      {
        "step_id": "1",
        "step_title": "Identify security vulnerabilities",
        "decomposition": "Scan code for vulnerabilities...",
        "estimated_time": 8,
        "primary_verb": "Identify",
        "deliverable": "List of 3 vulnerabilities",
        "novelty_hook": "constraint-output",
        "passion_anchor": "This determines system security",
        "urgency_cue": "Within your 8-minute window",
        "incup_tags": ["Passion"]
      }
    ]
  }
}
```

## API Documentation

Visit https://platform.gemini.com/docs for Gemini API documentation.

## Troubleshooting

- **Invalid API Key**: Ensure GEMINI_API_KEY is set correctly in .env
- **Module Imports**: Run from gemini/ directory or add to PYTHONPATH
- **Validation Errors**: Check step structure against AI Constitution rules
- **Insufficient Balance**: Ensure your Gemini account has credits
