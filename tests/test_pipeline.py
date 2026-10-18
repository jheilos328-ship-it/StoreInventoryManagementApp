import os
import unittest

os.environ["MOCK_OLLAMA"] = "1"

from app.inventory_engine import compute_metrics, detect_issues, normalize_inventory
from app.main import create_app
from app.service import build_actions


SAMPLE_INVENTORY = [
    {
        "product_id": "sku-123",
        "name": "Fast Widget",
        "stock": 5,
        "cost": 2.0,
        "price": 10.0,
        "sales_history": [1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    {
        "product_id": "sku-999",
        "name": "Slow Widget",
        "stock": 200,
        "cost": 1.5,
        "price": 5.0,
        "sales_history": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
]


class PipelineTest(unittest.TestCase):
    def test_inventory_pipeline_detects_issues(self):
        items = normalize_inventory(SAMPLE_INVENTORY)
        items_with_metrics = [{**item, "metrics": compute_metrics(item)} for item in items]
        issues = detect_issues(items_with_metrics)

        self.assertTrue(issues)
        self.assertTrue({issue["type"] for issue in issues} & {"overstock", "dead_stock"})

    def test_build_actions_returns_valid_action_cards(self):
        actions = build_actions(SAMPLE_INVENTORY)

        self.assertGreaterEqual(len(actions), 1)
        self.assertLessEqual(len(actions), 5)
        self.assertLessEqual(
            {"product", "action_type", "action", "why", "priority", "confidence", "metrics"},
            set(actions[0]),
        )

    def test_analyze_route_returns_actions(self):
        client = create_app().test_client()

        response = client.post("/analyze", json={"inventory": SAMPLE_INVENTORY})

        self.assertEqual(response.status_code, 200)
        self.assertIn("actions", response.get_json())


if __name__ == "__main__":
    unittest.main()
