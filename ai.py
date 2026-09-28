import os

import httpx

from models import BudgetRequest, BudgetSummary


OPENAI_COMPATIBLE = {
    "openai": (
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "gpt-4o-mini",
        "https://api.openai.com/v1/chat/completions",
    ),
    "groq": (
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
        "https://api.groq.com/openai/v1/chat/completions",
    ),
    "mistral": (
        "MISTRAL_API_KEY",
        "MISTRAL_MODEL",
        "mistral-small-latest",
        "https://api.mistral.ai/v1/chat/completions",
    ),
    "openrouter": (
        "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL",
        "google/gemini-2.0-flash-lite-001",
        "https://openrouter.ai/api/v1/chat/completions",
    ),
    "together": (
        "TOGETHER_API_KEY",
        "TOGETHER_MODEL",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "https://api.together.xyz/v1/chat/completions",
    ),
    "deepseek": (
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_MODEL",
        "deepseek-chat",
        "https://api.deepseek.com/chat/completions",
    ),
    "perplexity": (
        "PERPLEXITY_API_KEY",
        "PERPLEXITY_MODEL",
        "sonar",
        "https://api.perplexity.ai/chat/completions",
    ),
}

PROVIDERS = [
    "local",
    "gemini",
    "openai",
    "anthropic",
    "groq",
    "mistral",
    "cohere",
    "openrouter",
    "together",
    "deepseek",
    "perplexity",
]


def make_prompt(data: BudgetRequest, summary: BudgetSummary) -> str:
    categories = ", ".join(
        f"{name}: {amount:.2f}" for name, amount in summary.category_totals.items()
    )
    return (
        "You are PocketSmart AI, a careful budgeting assistant. Give a concise, "
        "practical monthly budget recommendation. Do not provide investment, tax, "
        "or legal advice. Use at most 140 words. "
        f"Currency: {data.currency}; income: {data.monthly_income:.2f}; "
        f"expenses: {summary.total_expenses:.2f}; remaining: {summary.remaining:.2f}; "
        f"savings goal: {data.savings_goal:.2f}; categories: {categories}."
    )


async def get_ai_advice(
    provider: str, data: BudgetRequest, summary: BudgetSummary
) -> str:
    provider = provider.lower()
    if provider == "local":
        return "Local analysis selected. The recommendations above require no API key."
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")

    prompt = make_prompt(data, summary)
    async with httpx.AsyncClient(timeout=30) as client:
        if provider == "gemini":
            return await _gemini(client, prompt)
        if provider == "anthropic":
            return await _anthropic(client, prompt)
        if provider == "cohere":
            return await _cohere(client, prompt)
        return await _openai_compatible(client, provider, prompt)


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not configured. Add it to your .env file.")
    return value


async def _gemini(client: httpx.AsyncClient, prompt: str) -> str:
    key = _required("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    response = await client.post(
        url,
        params={"key": key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


async def _openai_compatible(
    client: httpx.AsyncClient, provider: str, prompt: str
) -> str:
    key_env, model_env, default_model, url = OPENAI_COMPATIBLE[provider]
    response = await client.post(
        url,
        headers={"Authorization": f"Bearer {_required(key_env)}"},
        json={
            "model": os.getenv(model_env, default_model),
            "messages": [
                {"role": "system", "content": "Give safe, concise budgeting guidance."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


async def _anthropic(client: httpx.AsyncClient, prompt: str) -> str:
    response = await client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": _required("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            "max_tokens": 250,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


async def _cohere(client: httpx.AsyncClient, prompt: str) -> str:
    response = await client.post(
        "https://api.cohere.com/v2/chat",
        headers={"Authorization": f"Bearer {_required('COHERE_API_KEY')}"},
        json={
            "model": os.getenv("COHERE_MODEL", "command-r-08-2024"),
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    response.raise_for_status()
    return response.json()["message"]["content"][0]["text"]
