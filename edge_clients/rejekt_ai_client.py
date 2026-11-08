"""Optional server-side integration; do not call from browser code."""
import os
import httpx

async def call_edge_ai(task: str, input_text: str, context: str = "", max_tokens: int = 512) -> str:
    base = os.environ["REJEKT_EDGE_URL"].rstrip("/")
    key = os.environ["REJEKT_EDGE_KEY"]
    async with httpx.AsyncClient(timeout=150) as client:
        response = await client.post(
            f"{base}/v1/tasks",
            headers={"Authorization": f"Bearer {key}"},
            json={"task": task, "input": input_text, "context": context, "max_tokens": max_tokens},
        )
        response.raise_for_status()
        return response.json()["result"]
