from typing import Any, Dict, List

from app.config import CAP_DAYS_OF_STOCK, DEFAULT_TIME_WINDOW
from app.schemas import MetricsDict


def normalize_inventory(raw_inventory: Any) -> List[Dict[str, Any]]:
    items = []
    if isinstance(raw_inventory, dict):
        iter_items = raw_inventory.values()
    elif isinstance(raw_inventory, list):
        iter_items = raw_inventory
    else:
        iter_items = [raw_inventory]

    for src in iter_items:
        if not isinstance(src, dict):
            continue
        product_id = src.get("id") or src.get("product_id") or src.get("sku") or src.get("code")
        name = src.get("name") or src.get("title") or src.get("product_name") or ""
        stock = src.get("stock") or src.get("quantity") or src.get("on_hand") or 0
        cost = src.get("cost") or src.get("cost_price") or 0.0
        price = src.get("price") or src.get("sale_price") or src.get("retail_price") or 0.0
        sales_history = src.get("sales_history") or src.get("daily_sales") or src.get("sales") or []
        try:
            stock = float(stock)
        except Exception:
            stock = 0.0
        try:
            cost = float(cost)
        except Exception:
            cost = 0.0
        try:
            price = float(price)
        except Exception:
            price = 0.0
        cleaned_sales = []
        if isinstance(sales_history, list):
            for v in sales_history:
                try:
                    cleaned_sales.append(float(v))
                except Exception:
                    cleaned_sales.append(0.0)
        item = {
            "product_id": product_id,
            "name": name,
            "stock": stock,
            "cost": cost,
            "price": price,
            "sales_history": cleaned_sales,
        }
        items.append(item)
    return items


def compute_metrics(item: Dict[str, Any]) -> MetricsDict:
    sales = item.get("sales_history", [])
    data_coverage_days = len(sales)
    last_n = sales[-DEFAULT_TIME_WINDOW:] if data_coverage_days >= 1 else []
    velocity = sum(last_n) / max(len(last_n), 1)
    last_7 = sum(sales[-7:]) if data_coverage_days >= 1 else 0.0
    prev_7 = sum(sales[-14:-7]) if data_coverage_days >= 14 else 0.0
    if prev_7 > 0:
        trend = (last_7 - prev_7) / prev_7
    else:
        trend = 1.0 if last_7 > 0 else 0.0
    stock = float(item.get("stock", 0.0))
    price = float(item.get("price", 0.0))
    cost = float(item.get("cost", 0.0))
    raw_days = (stock / velocity) if velocity > 0 else CAP_DAYS_OF_STOCK
    if raw_days < 0:
        raw_days = 0.0
    days_of_stock = min(raw_days, CAP_DAYS_OF_STOCK)
    revenue_per_day = velocity * price
    gross_margin_per_day = (price - cost) * velocity
    metrics = {
        "velocity": float(velocity),
        "days_of_stock": float(days_of_stock),
        "revenue_per_day": float(revenue_per_day),
        "gross_margin_per_day": float(gross_margin_per_day),
        "trend": float(trend),
        "last_7": float(last_7),
        "prev_7": float(prev_7),
        "data_coverage_days": int(data_coverage_days),
    }
    return metrics


def detect_issues(items_with_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    for item in items_with_metrics:
        product = {"product_id": item.get("product_id"), "name": item.get("name")}
        metrics = item.get("metrics", {})
        velocity = metrics.get("velocity", 0.0)
        days = max(0.0, float(metrics.get("days_of_stock", CAP_DAYS_OF_STOCK)))
        trend = metrics.get("trend", 0.0)
        snapshot = {
            "metrics": {
                "velocity": float(metrics.get("velocity", 0.0)),
                "days_of_stock": float(days),
                "revenue_per_day": float(metrics.get("revenue_per_day", 0.0)),
                "trend": float(metrics.get("trend", 0.0)),
                "data_coverage_days": int(metrics.get("data_coverage_days", 0)),
            },
            "stock": float(item.get("stock", 0.0)),
            "cost": float(item.get("cost", 0.0)),
            "price": float(item.get("price", 0.0)),
        }
        if days < 5:
            severity_hint = 3 if days < 1 else (2 if days < 3 else 1)
            issues.append({
                "type": "stockout_risk",
                "product": product,
                "raw_metrics_snapshot": snapshot,
                "severity_hint": int(severity_hint),
            })
        if days > 90:
            severity_hint = 3 if days > 180 else (2 if days > 120 else 1)
            issues.append({
                "type": "overstock",
                "product": product,
                "raw_metrics_snapshot": snapshot,
                "severity_hint": int(severity_hint),
            })
        if float(trend) > 0.3:
            severity_hint = 3 if trend > 1.0 else (2 if trend > 0.6 else 1)
            issues.append({
                "type": "demand_spike",
                "product": product,
                "raw_metrics_snapshot": snapshot,
                "severity_hint": int(severity_hint),
            })
        if float(velocity) == 0.0 and float(item.get("stock", 0.0)) > 0:
            stock_qty = float(item.get("stock", 0.0))
            severity_hint = 2 if stock_qty > 50 else 1
            issues.append({
                "type": "dead_stock",
                "product": product,
                "raw_metrics_snapshot": snapshot,
                "severity_hint": int(severity_hint),
            })
    return issues
