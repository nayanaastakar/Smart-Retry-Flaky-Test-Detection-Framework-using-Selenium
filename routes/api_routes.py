from flask import Blueprint, jsonify, request, session
import json
import urllib.request
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
        "total": fetchone("SELECT COUNT(*) as c FROM executions")["c"],
        "passed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='pass'")["c"],
        "failed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='fail'")["c"],
        "flaky": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='flaky'")["c"],
    })

@api_bp.route("/generate-steps", methods=["POST"])
def generate_steps():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    sys_prompt = '''You are an expert QA automation engineer. Convert the user's natural language request into a JSON array of Selenium test steps. 
Return ONLY a valid JSON array. Do not include markdown formatting, backticks, or explanations.
Supported actions: open_url, click, type_text, press_key, assert_text, wait, screenshot.
Locator types: id, name, xpath, css, class.
You MUST guess the correct locators for popular websites (e.g. Amazon search bar is id=twotabsearchtextbox, Google is name=q, Myntra is class=desktop-searchBar).
Example output:
[
  {"action": "open_url", "input_value": "https://www.amazon.in"},
  {"action": "type_text", "locator_type": "id", "locator_value": "twotabsearchtextbox", "input_value": "shoes"},
  {"action": "press_key", "locator_type": "id", "locator_value": "twotabsearchtextbox", "input_value": "ENTER"},
  {"action": "screenshot"}
]'''

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": f"{sys_prompt}\n\nUser request: {prompt}",
        "stream": False,
        "format": "json"
    }
    
    req = urllib.request.Request(
        f"{settings.OLLAMA_HOST}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            response_json_text = result.get("response", "[]").strip()
            # fallback if model returns backticks
            if response_json_text.startswith("```json"):
                response_json_text = response_json_text[7:-3]
            elif response_json_text.startswith("```"):
                response_json_text = response_json_text[3:-3]
            
            steps = json.loads(response_json_text)
            if not isinstance(steps, list):
                steps = [steps]
            return jsonify({"steps": steps})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
