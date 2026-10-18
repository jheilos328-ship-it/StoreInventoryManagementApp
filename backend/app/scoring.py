from typing import Dict, Any
from math import sqrt

from app.config import CAP_DAYS_OF_STOCK, DEFAULT_TIME_WINDOW


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)
    except ValueError:
        return float(default)


def score_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Compute and attach deterministic scoring fields to an issue.

    - Uses only `raw_metrics_snapshot` and severity_hint.
    - Adds: final_score, impact_score, urgency_multiplier, trend_multiplier, confidence_multiplier
    - Stockout scoring increases as days_of_stock decreases (inverse behavior).
    - Dead/overstock impact scaled with sqrt to avoid domination.
    """
    snap = issue.get("raw_metrics_snapshot", {})
    metrics = snap.get("metrics", {})
    velocity = _safe_float(metrics.get("velocity", 0.0))
    days = _safe_float(metrics.get("days_of_stock", CAP_DAYS_OF_STOCK))
    revenue_per_day = _safe_float(metrics.get("revenue_per_day", 0.0))
    trend = _safe_float(metrics.get("trend", 0.0))
    coverage = int(metrics.get("data_coverage_days", 0) or 0)
    stock = _safe_float(snap.get("stock", 0.0))
    cost = _safe_float(snap.get("cost", 0.0))

    confidence_multiplier = min(float(coverage) / float(DEFAULT_TIME_WINDOW), 1.0) if DEFAULT_TIME_WINDOW>0 else 1.0

    t = issue.get("type")
    impact_score = 0.0
    urgency_multiplier = 1.0
    trend_multiplier = 1.0

    # Stockout: inverse days weighting
    if t == "stockout_risk":
        # fewer days => larger multiplier. add small epsilon to avoid div-by-zero
        inv_days = 1.0 / (days + 0.1)
        impact_score = revenue_per_day * (1.0 + inv_days)
        # urgency stronger when days small
        if days < 1:
            urgency_multiplier = 1.5
        elif days < 3:
            urgency_multiplier = 1.2
        else:
            urgency_multiplier = 1.0

    elif t == "overstock":
        # scale impact by sqrt to reduce huge domination
        raw = stock * cost
        impact_score = sqrt(max(0.0, raw))
        if days > 180:
            urgency_multiplier = 1.0
        elif days > 120:
            urgency_multiplier = 0.7
        else:
            urgency_multiplier = 0.4

    elif t == "dead_stock":
        raw = stock * cost
        impact_score = sqrt(max(0.0, raw)) * 0.9
        urgency_multiplier = 0.6

    elif t == "demand_spike":
        impact_score = revenue_per_day * 7.0
        trend_multiplier = 1.5 if trend > 0.5 else 1.2

    # trend multiplier smoothing
    if trend > 0.3:
        trend_multiplier = max(trend_multiplier, 1.2)
    elif trend < -0.2:
        trend_multiplier = 0.8

    final_score = float(impact_score) * float(urgency_multiplier) * float(trend_multiplier) * float(confidence_multiplier)
    if final_score != final_score or final_score == float('inf') or final_score < 0:
        final_score = 0.0

    # attach deterministic evidence
    evidence = {
        "days_of_stock": float(days),
        "velocity": float(velocity),
        "revenue_per_day": float(revenue_per_day),
        "score_components": {
            "impact_score": float(impact_score),
            "urgency_multiplier": float(urgency_multiplier),
            "trend_multiplier": float(trend_multiplier),
            "confidence_multiplier": float(confidence_multiplier),
        },
    }

    return {
        "final_score": float(final_score),
        "impact_score": float(impact_score),
        "urgency_multiplier": float(urgency_multiplier),
        "trend_multiplier": float(trend_multiplier),
        "confidence_multiplier": float(confidence_multiplier),
        "evidence": evidence,
    }
