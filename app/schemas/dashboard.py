from pydantic import BaseModel


class SummaryResponse(BaseModel):
    """High-level financial overview for the dashboard."""
    total_income: float
    total_expenses: float
    net_balance: float
    record_count: int


class CategoryTotal(BaseModel):
    category: str
    total: float
    count: int


class CategoryBreakdownResponse(BaseModel):
    income_by_category: list[CategoryTotal]
    expense_by_category: list[CategoryTotal]


class MonthlyTrend(BaseModel):
    month: str  # format: "2024-01"
    income: float
    expense: float
    net: float


class TrendsResponse(BaseModel):
    trends: list[MonthlyTrend]
