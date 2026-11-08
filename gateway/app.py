"""Device Mesh AI: authenticated laptop gateway for PrivateLM phone inference."""
import asyncio
import hmac
import os
import time
from typing import Literal
import httpx
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Device Mesh AI Gateway", version="0.1.0", docs_url=None, redoc_url=None)

class Phone:
    def __init__(self, name, url, token):
        self.name = name
        self.url = url.rstrip("/")
        self.token = token
        self.lock = asyncio.Lock()
        self.failures = 0
        self.cooldown_until = 0.0

def load_phones():
    result = []
    for number in (1, 2):
        url = os.getenv(f"PHONE_{number}_URL", "").strip()
        key = os.getenv(f"PHONE_{number}_KEY", "").strip()
        if url:
            if not url.startswith(("http://", "https://")):
                raise RuntimeError(f"PHONE_{number}_URL must start with http(s)://")
            if not key:
                raise RuntimeError(f"PHONE_{number}_KEY is required")
            result.append(Phone(f"phone-{number}", url, key))
    return result

phones = load_phones()

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
    return {"status": "running", "configured_phones": len(phones)}

@app.get("/v1/nodes", dependencies=[Depends(authorized)])
async def nodes():
    results = []
    async with httpx.AsyncClient(timeout=3) as client:
        for phone in phones:
            try:
                response = await client.get(phone.url + "/health")
                online = response.status_code == 200
            except httpx.HTTPError:
                online = False
            results.append({
                "name": phone.name, "online": online,
                "busy": phone.lock.locked(),
                "cooldown": max(0, round(phone.cooldown_until - time.monotonic()))
            })
    return {"nodes": results}

@app.post("/v1/tasks", dependencies=[Depends(authorized)])
async def run_task(payload: TaskRequest):
    if not phones:
        raise HTTPException(503, "No phone nodes configured")
    candidates = [p for p in phones if not p.lock.locked() and p.cooldown_until <= time.monotonic()]
    if not candidates:
        raise HTTPException(503, "All AI nodes busy or unavailable")
    timeout = float(os.getenv("PHONE_TIMEOUT_SEC", "120"))
    for phone in sorted(candidates, key=lambda p: (p.failures, p.name)):
        async with phone.lock:
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
                        phone.url + "/v1/chat/completions",
                        json=request,
                        headers={"Authorization": f"Bearer {phone.token}"}
                    )
                if response.status_code == 429 or response.status_code >= 500:
                    phone.failures += 1
                    phone.cooldown_until = time.monotonic() + 10
                    continue
                if response.status_code != 200:
                    raise HTTPException(502, f"Phone rejected request: HTTP {response.status_code}")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                phone.failures = 0
                return {
                    "task": payload.task, "result": content,
                    "node": phone.name, "model": data.get("model", "unknown")
                }
            except (httpx.HTTPError, KeyError, IndexError, ValueError):
                phone.failures += 1
                phone.cooldown_until = time.monotonic() + 10
    raise HTTPException(503, "No phone completed the inference request")
