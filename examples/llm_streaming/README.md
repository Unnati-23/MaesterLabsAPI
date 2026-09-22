# MaesterLabsAPI — LLM Streaming Endpoint

A real, runnable example that streams a language model's response to the client
**token-by-token** using Server-Sent Events (SSE). This is a Maester Labs
addition on top of the base framework.

## Why it matters

Chat UIs feel instant because tokens appear as they are generated instead of
waiting for the full response. This example shows the pattern with FastAPI's
`StreamingResponse` and an async generator.

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then try it:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain what an API is in one sentence."}'
```

- **Without** `ANTHROPIC_API_KEY`: a built-in mock stream runs, so the endpoint
  works out of the box.
- **With** `ANTHROPIC_API_KEY` set: real Claude output is streamed live.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export MAESTER_LLM_MODEL=claude-sonnet-5   # optional, this is the default
```

## Endpoints

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| GET    | `/`            | Health check + current config            |
| POST   | `/chat/stream` | Stream a model response as SSE           |
