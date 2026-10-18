import json
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, jsonify, make_response, request

from app.service import build_actions

api = Blueprint("api", __name__)


@api.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "Inventory Decision Advisor running"})


@api.route("/inventory", methods=["GET"])
def get_inventory():
    inventory_path = Path(__file__).resolve().parents[1] / "inventory.json"
    try:
        data = json.loads(inventory_path.read_text(encoding="utf-8"))
        return jsonify({"inventory": data})
    except FileNotFoundError:
        return make_response(jsonify({"error": "inventory.json not found"}), 404)
    except json.JSONDecodeError as error:
        return make_response(jsonify({"error": "invalid inventory.json", "detail": str(error)}), 500)
    except Exception as error:
        return make_response(jsonify({"error": "failed to read inventory", "detail": str(error)}), 500)


def validate_request_json(req) -> tuple[bool, Dict[str, Any]]:
    if not req.is_json:
        return False, {"error": "Invalid request: expected JSON body"}
    data = req.get_json(silent=True)
    if not data or "inventory" not in data:
        return False, {"error": "Invalid JSON: missing 'inventory' key"}
    return True, data


@api.route("/analyze", methods=["POST"])
def analyze():
    ok, data_or_error = validate_request_json(request)
    if not ok:
        return make_response(jsonify(data_or_error), 400)

    try:
        actions = build_actions(data_or_error["inventory"])
    except RuntimeError as error:
        try:
            detail = json.loads(str(error))
        except Exception:
            detail = {"error": str(error)}
        return make_response(jsonify(detail), 502)
    except ValueError as error:
        return make_response(jsonify({"error": str(error)}), 502)
    except Exception as error:
        return make_response(jsonify({"error": "analysis failed", "detail": str(error)}), 500)

    return make_response(jsonify({"actions": actions}), 200)
