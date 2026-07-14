import google.genai as genai
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

candidate_models = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.0-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview"
]

print("=== Testing Models ===")
for m in candidate_models:
    try:
        response = client.models.generate_content(
            model=m,
            contents="Say hello"
        )
        print(f"SUCCESS {m}: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED {m}: {e}")
