# AI Proxy Backend

AI Proxy Backend is a small Flask API prototype that routes a single user prompt to multiple AI providers and returns the responses in one JSON payload.

It was built as an experimental backend layer for AI-powered apps, especially prototypes that need to compare or combine responses from Claude, ChatGPT/OpenAI, and Gemini without exposing API keys directly in the frontend.

---

## Project Status

**Status:** Backend MVP / prototype  
**Framework:** Flask  
**Language:** Python  
**Storage:** SQLite for simple daily usage tracking  
**Primary Use Case:** Multi-provider AI backend for app prototypes

This is an early backend experiment and should be treated as a prototype, not a production-ready service.

---

## What It Does

The app exposes a `/query` endpoint that accepts a prompt and a list of AI providers to call.

Supported providers in the prototype:

- Claude / Anthropic
- ChatGPT / OpenAI
- Gemini / Google Generative AI

The backend returns a JSON response containing the available AI responses plus basic usage information.

---

## API Endpoints

### `POST /query`

Main endpoint for sending a prompt to selected AI providers.

Example request:

```json
{
  "prompt": "Explain this idea in simple terms.",
  "ais": ["claude", "chatgpt", "gemini"]
}
```

Example response shape:

```json
{
  "results": {
    "claude": "...",
    "chatgpt": "...",
    "gemini": "..."
  },
  "usage": {
    "used": 1,
    "limit": 10,
    "remaining": 9
  }
}
```

### `GET /health`

Health check endpoint.

```json
{
  "status": "ok"
}
```

---

## Key Features

- Flask API server
- CORS enabled for frontend/app access
- Environment-variable API key handling
- Anthropic, OpenAI, and Gemini client setup
- Simple per-user daily rate limiting
- SQLite usage tracking
- JSON response format for frontend integration

---

## Tech Stack

- Python
- Flask
- Flask-CORS
- SQLite
- Anthropic SDK
- OpenAI SDK
- Google Generative AI SDK
- Gunicorn

Dependencies are listed in `requirements.txt`.

---

## Environment Variables

This app expects API keys to be provided through environment variables:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

Do not commit real API keys to GitHub.

---

## Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

On Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="your_anthropic_key_here"
$env:OPENAI_API_KEY="your_openai_key_here"
$env:GOOGLE_API_KEY="your_google_key_here"
```

### 3. Start the server

```bash
python app.py
```

The app runs locally at:

```text
http://localhost:5000
```

---

## Example Curl Request

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Give me three app ideas.","ais":["claude","chatgpt","gemini"]}'
```

---

## My Role

**Backend Prototyper • AI Integration Explorer • Product Systems Designer**

For this project, I explored:

- Designing a small AI backend layer
- Connecting multiple AI providers through one endpoint
- Keeping API keys server-side instead of exposing them in frontend code
- Adding basic usage/rate limiting
- Returning structured JSON for app integration
- Using Flask as a lightweight backend for AI app prototypes

---

## Portfolio Notes

This project demonstrates early backend thinking for AI applications. It is useful as a foundation for multi-model chat apps, AI comparison tools, local app backends, and prototype systems that need provider abstraction.

Future improvements could include:

- Provider configuration file
- Better error handling
- Streaming responses
- Authentication
- Deployment documentation
- Stronger rate limiting
- Updated model names and SDK compatibility checks
- Tests

---

## Safety / Security Note

This is a prototype. Before public deployment, the app should be reviewed for security, API cost controls, authentication, provider-specific quota handling, and production-safe error behavior.
