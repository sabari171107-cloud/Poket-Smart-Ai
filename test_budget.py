from app.models import BudgetRequest, Expense
from app.services.budget import analyze_budget, local_recommendations


def sample_request() -> BudgetRequest:
    return BudgetRequest(
        monthly_income=50000,
        expenses=[
            Expense(category="Rent", amount=15000),
            Expense(category="Food", amount=5000),
        ],
        savings_goal=10000,
        provider="local",
    )


def test_budget_math():
    data = sample_request()
    result = analyze_budget(data)
    assert result.total_expenses == 20000
    assert result.remaining == 30000
    assert result.expense_ratio == 40
    assert result.savings_gap == 0
    assert result.status == "healthy"


def test_local_recommendations_are_available():
    data = sample_request()
    result = analyze_budget(data)
    assert len(local_recommendations(data, result)) >= 3
