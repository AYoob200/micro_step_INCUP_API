# Dopamine Coach - Gemini Provider with Flask API

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

### 3. Run Flask API Server

```bash
python API.py
```

The API will start on `http://localhost:5000`

## Project Structure

- `API.py` - Flask API server for task decomposition
- `decomposition_agent.py` - Core Gemini decomposition agent logic
- `config.py` - Gemini API configuration and settings
- `system_prompt.py` - AI Constitution and output specification
- `requirements.txt` - Python dependencies

## Configuration

All settings are managed in `config.py`:

- `API_PROVIDER`: Set to "gemini"
- `MODEL_ID`: Gemini model ("gemini-2.5-flash")
- `TEMPERATURE`: Creativity level (0.7 for balanced)
- `MAX_TOKENS`: Maximum response length (2000)
- `ENABLE_JSON_VALIDATION`: Enable output validation (True)

## API Usage

### Endpoints

#### POST `/decompose` - Decompose a task

Accepts a user intention and returns decomposed steps.

**Request:**

```json
{
  "user_input": "I need to redesign my database schema for better performance"
}
```

**Response:**

```json
{
  "task": {
    "task_id": 1,
    "task_title": "Redesign database schema for better performance",
    "task_priority": "High",
    "intent_priority": "High",
    "estimated_total_session_time": 120,
    "total_steps": 3,
    "steps": [...]
  }
}
```

#### GET `/health` - Health check

Returns the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "service": "Decomposition Agent API"
}
```

#### GET `/` - API documentation

Returns API documentation and available endpoints.

### Example Requests

**Using curl:**

```bash
# Decompose a task
curl -X POST http://localhost:5000/decompose \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Build an authentication system with OAuth2"}'

# Health check
curl http://localhost:5000/health

# View documentation
curl http://localhost:5000/
```

**Using Python requests:**

```python
import requests

response = requests.post(
    "http://localhost:5000/decompose",
    json={"user_input": "Set up a CI/CD pipeline"}
)
print(response.json())
```

## Output Format

All outputs are JSON-only (no markdown or UI formatting):

```json
{
  "task": {
    "task_id": 1,
    "task_title": "Refactor authentication system",
    "task_priority": "High",
    "intent_priority": "High",
    "estimated_total_session_time": 48,
    "total_steps": 3,
    "steps": [
      {
        "step_id": 1,
        "step_title": "Identify security vulnerabilities",
        "description": "Scan code for vulnerabilities...",
        "estimated_time": 8,
        "primary_verb": "Identify",
        "deliverable": "List of 3 vulnerabilities",
        "novelty_hook": "Learn security best practices",
        "passion_anchor": "This determines system security",
        "urgency_cue": "Within your 8-minute window",
        "incup_tags": "Passion"
      }
    ]
  }
}
```

## Troubleshooting

- **Invalid API Key**: Ensure GEMINI_API_KEY is set correctly in .env
- **Connection refused**: Make sure Flask API is running with `python API.py`
- **Port 5000 in use**: Change the port in API.py or kill the process using port 5000
- **Validation Errors**: Check step structure against AI Constitution rules
