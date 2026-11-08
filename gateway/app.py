"""Device Mesh AI: authenticated multi-platform local inference gateway."""
import asyncio
import hmac
import os
import time
from typing import Literal
import httpx
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Device Mesh AI Gateway", version="0.1.0", docs_url=None, redoc_url=None)

class Node:
    def __init__(self, name, url, token, platform="android"):
        self.name = name
        self.url = url.rstrip("/")
        self.token = token
        self.platform = platform
        self.lock = asyncio.Lock()
        self.failures = 0
        self.cooldown_until = 0.0

def load_nodes():
    """Load independent authenticated inference endpoints on Android, iOS, Windows or macOS.

    NODE_* variables take priority; old PHONE_* configuration is kept for compatibility.
    Nodes can run PrivateLM, llama.cpp server, or another OpenAI-compatible service.
    """
    result = []
    for number in range(1, 9):
        url = (os.getenv(f"NODE_{number}_URL")
               or (os.getenv(f"PHONE_{number}_URL") if number <= 2 else "")
               or "").strip()
        key = (os.getenv(f"NODE_{number}_KEY")
               or (os.getenv(f"PHONE_{number}_KEY") if number <= 2 else "")
               or "").strip()
        platform = os.getenv(f"NODE_{number}_PLATFORM", "android" if number <= 2 else "windows").lower()
        if url:
            if not url.startswith(("http://", "https://")):
                raise RuntimeError(f"NODE_{number}_URL must start with http(s)://")
            if not key:
                raise RuntimeError(f"NODE_{number}_KEY is required")
            if platform not in ("android", "ios", "windows", "macos", "linux"):
                raise RuntimeError(f"NODE_{number}_PLATFORM is invalid")
            result.append(Node(f"node-{number}", url, key, platform))
    return result

nodes = load_nodes()

async def authorized(authorization: str | None = Header(default=None)):
    expected = os.getenv("EDGE_API_KEY", "")
    if not expected:
        raise HTTPException(503, "EDGE_API_KEY not configured")
    if not authorization or not hmac.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(401, "Unauthorized")

class TaskRequest(BaseModel):
    task: Literal["resume_rewrite", "interview_prep", "general"]
    input: str = Field(min_length=1, max_length=12000)
    context: str = Field(default="", max_length=4000)
    max_tokens: int = Field(default=512, ge=16, le=2048)

PROMPTS = {
    "resume_rewrite": "Improve clarity and relevance of this resume while preserving all factual claims. Never invent work history, skills, numbers or credentials.",
    "interview_prep": "Provide concise interview practice based only on supplied facts. Do not invent work experience.",
    "general": "You assist with distributed AI workflows. Answer accurately and concisely.",
}

@app.get("/health")
async def health():
    return {"status": "running", "configured_nodes": len(nodes)}

@app.get("/v1/nodes", dependencies=[Depends(authorized)])
async def node_status():
    results = []
    async with httpx.AsyncClient(timeout=3) as client:
        for node in nodes:
            try:
                response = await client.get(node.url + "/health")
                online = response.status_code == 200
            except httpx.HTTPError:
                online = False
            results.append({
                "name": node.name, "online": online,
                "busy": node.lock.locked(), "platform": node.platform,
                "cooldown": max(0, round(node.cooldown_until - time.monotonic()))
            })
    return {"nodes": results}

@app.post("/v1/tasks", dependencies=[Depends(authorized)])
async def run_task(payload: TaskRequest):
    if not nodes:
        raise HTTPException(503, "No inference nodes configured")
    candidates = [p for p in nodes if not p.lock.locked() and p.cooldown_until <= time.monotonic()]
    if not candidates:
        raise HTTPException(503, "All AI nodes busy or unavailable")
    timeout = float(os.getenv("NODE_TIMEOUT_SEC", os.getenv("PHONE_TIMEOUT_SEC", "120")))
    for node in sorted(candidates, key=lambda p: (p.failures, p.name)):
        async with node.lock:
            request = {
                "model": "loaded-model", "stream": False,
                "max_tokens": payload.max_tokens,
                "messages": [
                    {"role": "system", "content": PROMPTS[payload.task]},
                    {"role": "user", "content": (payload.context + "\n\n" + payload.input).strip()}
                ]
            }
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        node.url + "/v1/chat/completions",
                        json=request,
                        headers={"Authorization": f"Bearer {node.token}"}
                    )
                if response.status_code == 429 or response.status_code >= 500:
                    node.failures += 1
                    node.cooldown_until = time.monotonic() + 10
                    continue
                if response.status_code != 200:
                    raise HTTPException(502, f"Node rejected request: HTTP {response.status_code}")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                node.failures = 0
                return {
                    "task": payload.task, "result": content,
                    "node": node.name, "model": data.get("model", "unknown")
                }
            except (httpx.HTTPError, KeyError, IndexError, ValueError):
                node.failures += 1
                node.cooldown_until = time.monotonic() + 10
    raise HTTPException(503, "No node completed the inference request")
