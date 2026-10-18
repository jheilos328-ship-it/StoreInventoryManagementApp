from typing import TypedDict, Dict, Any


class ProductDict(TypedDict, total=False):
    product_id: str
    name: str


class MetricsDict(TypedDict):
    velocity: float
    days_of_stock: float
    revenue_per_day: float
    trend: float
    data_coverage_days: int


class IssueDict(TypedDict, total=False):
    type: str
    product: ProductDict
    raw_metrics_snapshot: Dict[str, Any]
    severity_hint: int
    final_score: float
    impact_score: float
    urgency_multiplier: float
    trend_multiplier: float
    confidence_multiplier: float
    evidence: Dict[str, Any]
