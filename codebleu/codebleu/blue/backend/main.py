from flask import Flask, request, Response, render_template, jsonify
from evaluator import compute_codebleu_detailed
import os
import requests

app = Flask(__name__, template_folder="../frontend")

REPLICATE_URL = "https://api.replicate.com/v1/predictions"


def call_replicate(language: str, prompt: str):
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    debug = os.environ.get("REPLICATE_DEBUG")

    default_version = "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29f1c2684a2ef8fb3fe2cfe2993c3a765db8de"
    model_version = os.environ.get("REPLICATE_MODEL_VERSION", default_version)

    if not api_token:
        return 401, "REPLICATE_API_TOKEN not set in environment"

    system = (
        f"You are an expert {language} programmer. ONLY output valid, runnable {language} source code. "
        "Do NOT include explanations, markdown, or any extra text. If you cannot comply, output only ERROR_NO_CODE."
    )
    user = f"Task: {prompt}\n\nReturn only the code, nothing else."
    full_prompt = f"{system}\n\n{user}"

    payload = {
        "version": model_version,
        "input": {
            "prompt": full_prompt,
            "max_tokens": 1600,
            "temperature": 0.0,
            "top_p": 1.0,
        }
    }

    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(REPLICATE_URL, json=payload, headers=headers, timeout=120)
    except Exception as e:
        if debug:
            print("Replicate request failed:", e)
        return 502, f"Replicate request failed: {e}"

    if r.status_code not in (200, 201):
        return r.status_code, r.text

    try:
        data = r.json()
        if "output" in data:
            content = "".join(data["output"]).strip()
        else:
            content = str(data).strip()
    except Exception:
        return 502, "Failed to parse Replicate response"

    if debug:
        print("Replicate response:", content[:200])

    # Extract code from fenced blocks
    if "```" in content:
        parts = content.split("```")
        for i in range(1, len(parts), 2):
            chunk = parts[i]
            lines = chunk.splitlines()
            if lines and lines[0].strip().isalpha():
                code = "\n".join(lines[1:]).strip()
            else:
                code = chunk.strip()
            if code:
                return 200, code

    # Fallback code extraction based on keywords
    code_indicators = ("def ", "class ", "if __name__", "import ", "return ")
    if any(tok in content for tok in code_indicators):
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if any(tok in line for tok in code_indicators):
                return 200, "\n".join(lines[i:]).strip()

    return 200, content


def call_ollama(language: str, prompt: str):
    debug = os.environ.get("REPLICATE_DEBUG")
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    model = os.environ.get("OLLAMA_MODEL", "llama2")

    system = (
        f"You are an expert {language} programmer. ONLY output valid, runnable {language} source code. "
        "Do NOT include explanations, markdown, or any extra text. If you cannot comply, output only ERROR_NO_CODE."
    )
    user = f"Task: {prompt}\n\nReturn only the code, nothing else."

    payload = {
        "model": model,
        "prompt": f"{system}\n\n{user}",
        "max_tokens": 1600,
        "temperature": 0.0,
        "stream": False
    }

    try:
        r = requests.post(url, json=payload, timeout=120)
    except Exception as e:
        if debug:
            print("Ollama request failed:", e)
        return 502, f"Ollama request failed: {e}"

    if r.status_code != 200:
        return r.status_code, r.text

    try:
        data = r.json()
        content = data.get("response", "").strip()
    except Exception:
        return 502, "Failed to parse Ollama response"

    if debug:
        print("Ollama response:", content[:200])

    # Extract code in fences
    if "```" in content:
        parts = content.split("```")
        for i in range(1, len(parts), 2):
            chunk = parts[i]
            lines = chunk.splitlines()
            if lines and lines[0].strip().isalpha():
                code = "\n".join(lines[1:]).strip()
            else:
                code = chunk.strip()
            if code:
                return 200, code

    # Keyword-based extraction
    code_indicators = ("def ", "class ", "import ", "return ", ";", "{", "}")
    if any(tok in content for tok in code_indicators):
        return 200, content.strip()

    return 200, content


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    language = str(data.get("language", "python")).strip().lower()
    prompt = str(data.get("prompt", "")).strip()

    use_ollama = os.environ.get("USE_OLLAMA", "0") in ("1", "true", "True")

    # 1 — Try local Ollama first
    if use_ollama:
        status, body = call_ollama(language, prompt)
        if status == 200:
            return Response(body, mimetype="text/plain")

    # 2 — Try Replicate next
    status, body = call_replicate(language, prompt)
    if status == 200:
        return Response(body, mimetype="text/plain")

    # 3 — If both fail, return clean error
    return jsonify({"error": body}), status


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(silent=True) or {}
    reference = str(data.get("reference", ""))
    candidate = str(data.get("candidate", ""))
    language = str(data.get("language", "python")).lower().strip()
    result = compute_codebleu_detailed(reference, candidate, language)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
