from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Expense(BaseModel):
    category: str = Field(min_length=1, max_length=60)
    amount: float = Field(ge=0)

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str) -> str:
        return value.strip().title()


class BudgetRequest(BaseModel):
    monthly_income: float = Field(gt=0)
    expenses: list[Expense] = Field(min_length=1, max_length=50)
    savings_goal: float = Field(default=0, ge=0)
    provider: str = Field(default="local", max_length=30)
    currency: Literal["INR", "USD", "EUR", "GBP"] = "INR"


class BudgetSummary(BaseModel):
    total_expenses: float
    remaining: float
    expense_ratio: float
    savings_gap: float
    category_totals: dict[str, float]
    status: str


class BudgetResponse(BaseModel):
    summary: BudgetSummary
    recommendations: list[str]
    ai_advice: str
    provider_used: str
