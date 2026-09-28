from collections import defaultdict

from models import BudgetRequest, BudgetSummary


def analyze_budget(data: BudgetRequest) -> BudgetSummary:
    category_totals: dict[str, float] = defaultdict(float)
    for expense in data.expenses:
        category_totals[expense.category] += expense.amount

    total = round(sum(category_totals.values()), 2)
    remaining = round(data.monthly_income - total, 2)
    ratio = round((total / data.monthly_income) * 100, 1)
    savings_gap = round(max(data.savings_goal - max(remaining, 0), 0), 2)

    if remaining < 0:
        status = "over_budget"
    elif ratio > 80:
        status = "tight"
    else:
        status = "healthy"

    return BudgetSummary(
        total_expenses=total,
        remaining=remaining,
        expense_ratio=ratio,
        savings_gap=savings_gap,
        category_totals=dict(
            sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ),
        status=status,
    )


def local_recommendations(
    data: BudgetRequest, summary: BudgetSummary
) -> list[str]:
    tips: list[str] = []

    if summary.remaining < 0:
        tips.append(
            f"Reduce monthly spending by at least {abs(summary.remaining):,.2f} "
            "to stop running a deficit."
        )
    elif summary.expense_ratio > 80:
        tips.append(
            "Expenses exceed 80% of income. Review flexible costs before adding "
            "new commitments."
        )
    else:
        tips.append(
            "Your expenses are within a manageable range. Automate part of the "
            "remaining balance into savings."
        )

    if summary.category_totals:
        largest_name, largest_amount = next(iter(summary.category_totals.items()))
        tips.append(
            f"{largest_name} is your largest category at {largest_amount:,.2f}. "
            "Check it first for realistic reductions."
        )

    if summary.savings_gap > 0:
        tips.append(
            f"Your current surplus is short of the savings goal by "
            f"{summary.savings_gap:,.2f}. Lower the goal temporarily or reduce "
            "non-essential expenses."
        )
    elif data.savings_goal > 0:
        tips.append("Your current surplus can cover the stated savings goal.")

    tips.append(
        "Keep a small emergency buffer and review actual spending every week."
    )
    return tips
