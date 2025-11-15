# Ollama Setup Guide

## Step 1: Verify Ollama Installation
After Ollama finishes installing, open a new terminal and verify it's installed:
```
ollama --version
```

## Step 2: Start Ollama Server
In one terminal, start the Ollama server (this will listen on `http://127.0.0.1:11434`):
```
ollama serve
```

## Step 3: Download a Model (in a new terminal)
While the server is running, download a model. For code generation, good options are:
- **codellama** (Meta's code model; ~7B parameter version is reasonable on most machines):
  ```
  ollama pull codellama
  ```
- **llama2** (general-purpose, smaller):
  ```
  ollama pull llama2
  ```
- **neural-chat** (lightweight, fast):
  ```
  ollama pull neural-chat
  ```

Pick one. If you're unsure, start with `codellama` as it's optimized for code tasks.

**Note:** First pull may take a few minutes depending on model size and internet speed.

## Step 4: Verify the Model is Available
Check that the model loaded correctly:
```
ollama list
```
You should see your model listed (e.g., `codellama:latest`).

## Step 5: Configure Your App
In your command prompt (before starting the Flask server), set these environment variables:

**Windows cmd:**
```
set USE_OLLAMA=1
set OLLAMA_MODEL=codellama
set OPENAI_DEBUG=1
```

If you chose a different model name, replace `codellama` with your model name (e.g., `llama2`, `neural-chat`).

## Step 6: Start the Flask Server
Navigate to the backend folder and run:
```
cd c:\Users\User\blue\backend
python main.py
```

You should see Flask start on `0.0.0.0:8000`. The debug output will show:
- Whether Ollama requests succeed or fail.
- If Ollama is unavailable, it will fall back to OpenAI (if `OPENAI_API_KEY` is set).
- If both fail, it will use the local leap-year fallback for common prompts.

## Step 7: Test the Endpoint
Use any HTTP client (browser, curl, Postman, VS Code REST client, etc.) to test:

**Example using curl in a new terminal:**
```
curl -X POST http://localhost:8000/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"language\": \"python\", \"prompt\": \"leap year code\"}"
```

Expected output: full Python code for checking leap years (from Ollama or fallback).

---

## Troubleshooting

### Ollama Server Won't Start
- Make sure no other process is using port 11434.
- Try restarting Ollama.

### Model Pull Hangs or Fails
- Check your internet connection.
- Try a smaller model (e.g., `neural-chat` instead of `codellama`).

### Flask Can't Reach Ollama
- Verify Ollama server is running (`ollama serve` in another terminal).
- Check that `OLLAMA_URL` is correct: `http://127.0.0.1:11434/api/generate` (default).
- Look at `OPENAI_DEBUG=1` output for specific error messages.

### Code Looks Wrong or Templates Instead of Generated Code
- Check the debug output in the Flask terminal — it will show if Ollama succeeded.
- If Ollama fails, the app falls back to OpenAI → local fallback → error message.
- Try a different model or ensure the model is fully downloaded (`ollama list`).

---

## Environment Variables Cheat Sheet

| Variable | Default | Purpose |
|----------|---------|---------|
| `USE_OLLAMA` | `0` | Set to `1` to enable Ollama. |
| `OLLAMA_URL` | `http://127.0.0.1:11434/api/generate` | Ollama server endpoint. |
| `OLLAMA_MODEL` | `llama2` | Model name to use (must be downloaded). |
| `OPENAI_API_KEY` | (none) | OpenAI API key (fallback if Ollama fails). |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model name (fallback). |
| `OPENAI_DEBUG` | `0` | Set to `1` for detailed debug logs. |

---

## Quick Start Commands (Windows cmd)

Copy-paste this block into your terminal once Ollama is installed and you've pulled a model:

```
cd c:\Users\User\blue\backend
set USE_OLLAMA=1
set OLLAMA_MODEL=codellama
set OPENAI_DEBUG=1
python main.py
```

Then test:
```
curl -X POST http://localhost:8000/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"language\": \"python\", \"prompt\": \"leap year code\"}"
```

Good luck! 🚀
