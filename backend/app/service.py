import json
from typing import Any, Dict, List

from app.actions import actions_from_llm_result, issues_to_llm_payload, validate_actions_schema
from app.inventory_engine import compute_metrics, detect_issues, normalize_inventory
from app.llm_service import call_llm_with_issues
from app.ranking import select_top_diverse, sort_already_scored
from app.scoring import score_issue


def compute_metrics_for_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items_with_metrics = []
    for item in items:
        copy = dict(item)
        copy["metrics"] = compute_metrics(item)
        items_with_metrics.append(copy)
    return items_with_metrics


def score_issues_list(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = []
    for issue in issues:
        copy = dict(issue)
        copy.update(score_issue(issue))
        scored.append(copy)
    return scored


def select_top_issues(issues: List[Dict[str, Any]], count: int = 10) -> List[Dict[str, Any]]:
    return select_top_diverse(sort_already_scored(issues), k=count)


def build_actions(raw_inventory: Any) -> List[Dict[str, Any]]:
    items = normalize_inventory(raw_inventory)
    items_with_metrics = compute_metrics_for_items(items)
    issues = detect_issues(items_with_metrics)
    scored = score_issues_list(issues)
    top_issues = select_top_issues(scored, count=10)

    llm_ok, llm_result = call_llm_with_issues(issues_to_llm_payload(top_issues))
    if not llm_ok:
        raise RuntimeError(json.dumps(llm_result))

    actions = actions_from_llm_result(llm_result, top_issues)
    valid, reason = validate_actions_schema(actions)
    if not valid:
        raise ValueError(f"Invalid actions schema from LLM: {reason}")

    return actions[:5]
