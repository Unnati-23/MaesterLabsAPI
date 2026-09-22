"""MaesterLabsAPI — LLM Streaming Endpoint.

A production-style example that streams a language model's response to the
client token-by-token using Server-Sent Events (SSE). This is functionality
that vanilla FastAPI does not ship with — it is a Maester Labs addition.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs and try POST /chat/stream, or:
    curl -N -X POST http://127.0.0.1:8000/chat/stream \\
         -H "Content-Type: application/json" \\
         -d '{"prompt": "Explain what an API is in one sentence."}'

If ANTHROPIC_API_KEY is set in the environment, real Claude output is streamed.
Otherwise a built-in mock stream runs so the endpoint works out of the box.
"""

import asyncio
import json
import os
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="MaesterLabsAPI — LLM Streaming",
    description="Stream language-model responses token-by-token over SSE.",
    version="0.1.0",
)

# Model is configurable; defaults to Maester Labs' preferred Claude model.
MODEL = os.environ.get("MAESTER_LLM_MODEL", "claude-sonnet-5")


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="The user's message to send to the model.")
    max_tokens: int = Field(512, ge=1, le=4096, description="Response length cap.")


def _sse(data: str) -> str:
    """Format a chunk as a Server-Sent Event frame."""
    return f"data: {json.dumps({'token': data})}\n\n"


async def _mock_stream(prompt: str) -> AsyncGenerator[str, None]:
    """Fallback stream so the endpoint runs without an API key."""
    reply = (
        f"[mock] You said: {prompt!r}. "
        "Set ANTHROPIC_API_KEY to stream real Claude responses."
    )
    for word in reply.split(" "):
        await asyncio.sleep(0.05)
        yield _sse(word + " ")
    yield "data: [DONE]\n\n"


async def _claude_stream(req: ChatRequest) -> AsyncGenerator[str, None]:
    """Stream real tokens from Claude via the Anthropic SDK."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY from the environment
    async with client.messages.stream(
        model=MODEL,
        max_tokens=req.max_tokens,
        messages=[{"role": "user", "content": req.prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield _sse(text)
    yield "data: [DONE]\n\n"


@app.get("/")
async def health() -> dict:
    return {"status": "ok", "model": MODEL, "live_llm": bool(os.environ.get("ANTHROPIC_API_KEY"))}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """Stream a model response as Server-Sent Events."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        generator = _claude_stream(req)
    else:
        generator = _mock_stream(req.prompt)
    return StreamingResponse(generator, media_type="text/event-stream")
