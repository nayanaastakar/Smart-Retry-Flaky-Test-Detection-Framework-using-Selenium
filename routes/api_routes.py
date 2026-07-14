from flask import Blueprint, jsonify, request
import json
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
    """Use the official google-genai SDK (supports AQ keys) to generate Selenium test steps."""
    data = request.get_json() or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not set in .env"}), 500

    system_instruction = (
        "You are an expert QA automation engineer. "
        "Convert the user's natural language request into a JSON array of Selenium test steps. "
        "Return ONLY a raw JSON array — no markdown, no backticks, no explanation, no extra text at all. "
        "Each step is a JSON object with these fields:\n"
        "  action (required): one of open_url, type_text, press_key, click, assert_text, wait, screenshot\n"
        "  locator_type (optional): one of id, name, xpath, css, class\n"
        "  locator_value (optional): the locator string\n"
        "  input_value (optional): value to type, URL, key name, or text to assert\n"
        "  timeout (optional): integer, default 10\n\n"
        "You MUST infer the correct locators for well-known websites:\n"
        "- Google / google.com: search bar → name=q\n"
        "- Amazon / amazon.in: search bar → id=twotabsearchtextbox\n"
        "- Flipkart: search bar → name=q\n"
        "- Myntra: search bar → class=desktop-searchBar\n"
        "- Wikipedia: search bar → name=search\n"
        "- YouTube: search bar → name=search_query\n"
        "- OrangeHRM: username → name=username, password → name=password, submit → xpath=//button[@type='submit']\n"
        "- Naukri: search bar → id=searchText\n"
        "- LinkedIn: search bar → xpath=//input[contains(@class,'search-global-typeahead__input')]\n"
        "Rules:\n"
        "1. First step MUST be open_url with the full https:// URL\n"
        "2. Last step MUST be screenshot\n"
        "3. After press_key ENTER on a search, add a wait step: {\"action\":\"wait\",\"input_value\":\"2\",\"timeout\":10}\n"
        "4. All timeouts must be 10\n"
        "5. For login flows, include open_url, type username, type password, click submit, screenshot\n"
    )

    full_prompt = f"{system_instruction}\n\nUser request: {prompt}"

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=full_prompt,
        )

        raw_text = response.text.strip()

        # Strip markdown fences if the model added them
        if raw_text.startswith("```"):
            parts = raw_text.split("```")
            raw_text = parts[1]
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

    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned invalid JSON: {e}. Raw output: {raw_text[:300]}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
