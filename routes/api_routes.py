from flask import Blueprint, jsonify, request
import json
import urllib.request
import urllib.error
from config import settings
from database.db_manager import fetchall, fetchone, execute

api_bp = Blueprint("api", __name__)


@api_bp.route("/executions")
def executions():
    rows = fetchall("SELECT * FROM executions ORDER BY started_at DESC LIMIT 50")
    return jsonify([dict(r) for r in rows])


@api_bp.route("/projects")
def projects():
    rows = fetchall("SELECT * FROM projects ORDER BY created_at DESC")
    return jsonify([dict(r) for r in rows])


@api_bp.route("/stats")
def stats():
    return jsonify({
        "total":  fetchone("SELECT COUNT(*) as c FROM executions")["c"],
        "passed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='pass'")["c"],
        "failed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='fail'")["c"],
        "flaky":  fetchone("SELECT COUNT(*) as c FROM executions WHERE status='flaky'")["c"],
    })


@api_bp.route("/generate-steps", methods=["POST"])
def generate_steps():
    """Use Google Gemini API to convert a natural language prompt into Selenium test steps."""
    data = request.get_json() or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not configured in .env"}), 500

    system_instruction = (
        "You are an expert QA automation engineer. "
        "Convert the user's natural language request into a JSON array of Selenium test steps. "
        "Return ONLY a raw JSON array — no markdown, no backticks, no explanation. "
        "Each step must have: action, and optionally locator_type, locator_value, input_value, timeout. "
        "Supported actions: open_url, type_text, press_key, click, assert_text, wait, screenshot. "
        "Locator types: id, name, xpath, css, class. "
        "You MUST infer the correct locators for well-known websites:\n"
        "- Google: search bar is name=q\n"
        "- Amazon / amazon.in: search bar is id=twotabsearchtextbox\n"
        "- Flipkart: search bar is name=q\n"
        "- Myntra: search bar is class=desktop-searchBar\n"
        "- Wikipedia: search bar is name=search\n"
        "- YouTube: search bar is name=search_query\n"
        "- For any other website: inspect common patterns (id=search, name=q, etc.)\n"
        "IMPORTANT: The first step must ALWAYS be open_url with the full URL. "
        "Always end with a screenshot step. "
        "Timeouts should all be 10. "
        "Example for 'go to google and search for cats':\n"
        '[{"action":"open_url","input_value":"https://www.google.com","timeout":10},'
        '{"action":"type_text","locator_type":"name","locator_value":"q","input_value":"cats","timeout":10},'
        '{"action":"press_key","locator_type":"name","locator_value":"q","input_value":"ENTER","timeout":10},'
        '{"action":"wait","input_value":"2","timeout":10},'
        '{"action":"screenshot","timeout":10}]'
    )

    gemini_payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_instruction}\n\nUser request: {prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        }
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={api_key}"
    )

    req = urllib.request.Request(
        url,
        data=json.dumps(gemini_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=settings.AI_REQUEST_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # Extract the text content from Gemini response
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        steps = json.loads(raw_text)
        if not isinstance(steps, list):
            steps = [steps]

        # Ensure every step has a timeout
        for step in steps:
            step.setdefault("timeout", 10)

        return jsonify({"steps": steps})

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return jsonify({"error": f"Gemini API error {e.code}: {body}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
