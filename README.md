# PocketSmart AI

A FastAPI budgeting assistant with deterministic calculations and optional
recommendations from 10 AI providers.

## Features

- Monthly income, expense, and savings-goal analysis
- Category totals, remaining balance, spending ratio, and savings gap
- Useful local recommendations that work without an API key
- Gemini, OpenAI, Anthropic, Groq, Mistral, Cohere, OpenRouter, Together,
  DeepSeek, and Perplexity integrations
- Async provider calls with HTTPX
- Responsive Jinja2 interface
- API validation, error handling, health check, tests, and Docker deployment

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. API documentation is available at
<http://127.0.0.1:8000/docs>.

The default `local` provider works immediately. To use an AI provider, add its
key to `.env`, restart the server, and choose it in the interface. Never commit
the `.env` file.

## Test

```bash
pytest -q
```

## Deploy

### Render

1. Push this folder to GitHub.
2. Create a Render Blueprint using `render.yaml`, or create a Docker web service.
3. Add the desired API keys as secret environment variables in Render.
4. Deploy and verify `/health`.

### Docker

```bash
docker build -t pocketsmart-ai .
docker run --env-file .env -p 8000:8000 pocketsmart-ai
```

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_income": 50000,
    "expenses": [
      {"category": "Rent", "amount": 15000},
      {"category": "Food", "amount": 6000}
    ],
    "savings_goal": 10000,
    "provider": "local",
    "currency": "INR"
  }'
```

## Suggested epic completion

- **Prerequisites:** Install Python/Git, create a virtual environment, and add
  provider keys to `.env`.
- **Epic 1:** Verify Gemini with one `/api/analyze` request.
- **Epic 2:** Validate budget math and local recommendations.
- **Epic 3:** Verify FastAPI routes, validation, docs, and provider errors.
- **Epic 4:** Test the interface on desktop and mobile.
- **Epic 5:** Run `pytest`, push to GitHub, deploy, and add demo/repository links.

> PocketSmart provides educational budgeting guidance, not professional
> financial, investment, tax, or legal advice.