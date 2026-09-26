from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import BudgetRequest, BudgetResponse
from app.services.ai import PROVIDERS, get_ai_advice
from app.services.budget import analyze_budget, local_recommendations

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="PocketSmart AI",
    description="Smart budget analysis and multi-provider AI recommendations.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"providers": PROVIDERS},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/providers")
async def providers():
    return {"providers": PROVIDERS}


@app.post("/api/analyze", response_model=BudgetResponse)
async def analyze(data: BudgetRequest):
    summary = analyze_budget(data)
    recommendations = local_recommendations(data, summary)
    try:
        advice = await get_ai_advice(data.provider, data, summary)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        detail = f"{data.provider.title()} API returned an error."
        raise HTTPException(status_code=502, detail=detail) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, detail="The selected AI provider is unavailable."
        ) from exc

    return BudgetResponse(
        summary=summary,
        recommendations=recommendations,
        ai_advice=advice,
        provider_used=data.provider,
    )
