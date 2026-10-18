from typing import List, Dict, Any

#diversity caps
CAPS = {
    "dead_stock": 2,
    "overstock": 2,
}


def sort_already_scored(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assumes each issue has `final_score` attached. Sorts deterministically."""
    def key(i: Dict[str, Any]):
        fs = float(i.get("final_score", 0.0) or 0.0)
        pid = ""
        prod = i.get("product") or {}
        if isinstance(prod, dict):
            pid = prod.get("product_id") or prod.get("name") or ""
        elif isinstance(prod, str):
            pid = prod
        return (-fs, str(pid))

    return sorted(issues, key=key)


def select_top_diverse(issues: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
    sorted_issues = sort_already_scored(issues)
    out = []
    counts = {}
    #ensure at least one stockout if exists
    stockout_exists = next((i for i in sorted_issues if i.get("type") == "stockout_risk"), None)

    for it in sorted_issues:
        if len(out) >= k:
            break
        t = it.get("type")
        c = counts.get(t, 0)
        cap = CAPS.get(t, k)
        if c >= cap:
            continue
        out.append(it)
        counts[t] = c + 1

    #if no stockout included but exists, ensure it appears
    if stockout_exists and not any(i.get("type") == "stockout_risk" for i in out):
        #replace last non-stockout with top stockout
        for idx in range(len(out)-1, -1, -1):
            if out[idx].get("type") != "stockout_risk":
                out[idx] = stockout_exists
                break

    return out[:k]
