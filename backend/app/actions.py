from typing import Any, Dict, List

from app.config import ALLOWED_ACTION_TYPES, CAP_DAYS_OF_STOCK, DECISION_TAXONOMY, DEFAULT_TIME_WINDOW


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return float(default)
    if number != number or number in (float("inf"), -float("inf")):
        return float(default)
    return number


def priority_from_score(score: float) -> str:
    if score >= 100.0:
        return "high"
    if score >= 20.0:
        return "medium"
    return "low"


def confidence_from_coverage(coverage_days: int) -> str:
    if coverage_days >= DEFAULT_TIME_WINDOW:
        return "high"
    if coverage_days >= max(1, DEFAULT_TIME_WINDOW // 2):
        return "medium"
    return "low"


def issues_to_llm_payload(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payload = []
    for issue in issues:
        issue_type = issue.get("type")
        product = issue.get("product") or {}
        metrics = (issue.get("raw_metrics_snapshot") or {}).get("metrics", {})

        product_id = product.get("product_id") if isinstance(product, dict) else product
        product_name = product.get("name") if isinstance(product, dict) else product

        payload.append({
            "action_type": DECISION_TAXONOMY.get(issue_type, "monitor"),
            "product": {
                "product_id": product_id,
                "name": product_name,
            },
            "metrics": {
                "velocity": safe_float(metrics.get("velocity", 0.0)),
                "days_of_stock": min(max(safe_float(metrics.get("days_of_stock", CAP_DAYS_OF_STOCK)), 0.0), CAP_DAYS_OF_STOCK),
                "revenue_per_day": safe_float(metrics.get("revenue_per_day", 0.0)),
                "trend": safe_float(metrics.get("trend", 0.0)),
                "data_coverage_days": int(metrics.get("data_coverage_days", 0) or 0),
            },
            "score": safe_float(issue.get("final_score", 0.0)),
            "reason_code": issue_type,
        })
    return payload


def convert_issues_to_actions(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for issue in issues:
        product = issue.get("product") or {}
        if isinstance(product, dict):
            product_name = product.get("name") or product.get("product_id") or "unknown"
        else:
            product_name = product or "unknown"

        metrics = issue.get("metrics") or (issue.get("raw_metrics_snapshot") or {}).get("metrics", {})
        score = safe_float(issue.get("score", issue.get("final_score", 0.0)))
        coverage_days = int(metrics.get("data_coverage_days", 0) or 0)

        action_type = issue.get("action_type") or DECISION_TAXONOMY.get(issue.get("reason_code") or issue.get("type"), "monitor")
        if action_type not in ALLOWED_ACTION_TYPES:
            action_type = "monitor"

        priority = issue.get("priority") or priority_from_score(score)
        if priority not in {"high", "medium", "low"}:
            priority = priority_from_score(score)

        confidence = issue.get("confidence") or confidence_from_coverage(coverage_days)
        if confidence not in {"high", "medium", "low"}:
            confidence = confidence_from_coverage(coverage_days)

        actions.append({
            "product": str(product_name),
            "action_type": action_type,
            "action": str(issue.get("action") or f"{action_type.replace('_', ' ').capitalize()} for {product_name}"),
            "why": str(issue.get("why") or f"reason: {issue.get('reason_code') or issue.get('type') or 'issue'}; score={round(score, 2)}"),
            "priority": priority,
            "confidence": confidence,
            "metrics": {
                "velocity": safe_float(metrics.get("velocity", 0.0)),
                "days_of_stock": min(max(safe_float(metrics.get("days_of_stock", CAP_DAYS_OF_STOCK)), 0.0), CAP_DAYS_OF_STOCK),
                "revenue_per_day": safe_float(metrics.get("revenue_per_day", 0.0)),
                "trend": safe_float(metrics.get("trend", 0.0)),
            },
        })
    return actions


def normalize_actions(actions: Any, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(actions, list):
        return []

    issue_by_product = {}
    for issue in issues:
        product = issue.get("product") or {}
        if isinstance(product, dict):
            for key in (product.get("product_id"), product.get("name")):
                if key:
                    issue_by_product[str(key)] = issue
        elif product:
            issue_by_product[str(product)] = issue

    normalized = []
    for action in actions:
        if not isinstance(action, dict):
            continue

        product = action.get("product")
        if isinstance(product, dict):
            product_name = product.get("name") or product.get("product_id")
        else:
            product_name = product
        product_name = str(product_name or action.get("product_id") or action.get("name") or "unknown")

        matched_issue = issue_by_product.get(product_name)
        source = dict(matched_issue or {})
        source.update(action)
        source["product"] = product_name

        metrics = action.get("metrics")
        if not isinstance(metrics, dict) and matched_issue:
            metrics = (matched_issue.get("raw_metrics_snapshot") or {}).get("metrics", {})
        source["metrics"] = metrics or {}

        normalized.extend(convert_issues_to_actions([source]))

    return normalized


def actions_from_llm_result(llm_result: Any, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(llm_result, dict):
        return []
    if isinstance(llm_result.get("actions"), list):
        return normalize_actions(llm_result["actions"], issues)
    if isinstance(llm_result.get("issues"), list):
        return convert_issues_to_actions(llm_result["issues"])
    return []


def validate_actions_schema(actions: Any) -> tuple[bool, str]:
    if not isinstance(actions, list):
        return False, "actions must be a list"

    for action in actions:
        if not isinstance(action, dict):
            return False, "each action must be an object"
        for key in ("product", "action_type", "action", "why", "priority", "confidence", "metrics"):
            if key not in action:
                return False, f"missing field in action: {key}"
        if action.get("action_type") not in ALLOWED_ACTION_TYPES:
            return False, "invalid action_type"
        if action.get("priority") not in {"high", "medium", "low"}:
            return False, "invalid priority"
        if action.get("confidence") not in {"high", "medium", "low"}:
            return False, "invalid confidence"
        if not isinstance(action.get("product"), str):
            return False, "product must be a string"
        if not isinstance(action.get("action"), str) or not isinstance(action.get("why"), str):
            return False, "action/why must be strings"

        metrics = action.get("metrics")
        if not isinstance(metrics, dict):
            return False, "metrics must be an object"
        for metric in ("velocity", "days_of_stock", "revenue_per_day", "trend"):
            try:
                value = float(metrics.get(metric))
            except Exception:
                return False, f"metrics.{metric} must be numeric"
            if value != value or value in (float("inf"), -float("inf")):
                return False, f"metrics.{metric} must be finite"
        if safe_float(metrics.get("days_of_stock", 0.0)) < 0:
            return False, "metrics.days_of_stock must be >= 0"

    return True, ""
