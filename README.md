# Device Mesh AI

Standalone experimental inference cluster connecting a Windows/Linux laptop coordinator to two Android phones. **Not part of the rejekt.ai repository.**

## Hardware
- Lenovo IdeaPad (8th-gen Intel Core i5, 12 GB RAM, 256 GB SSD + 1 TB HDD): coordinator and API gateway
- Android phone 1 and 2 (8 GB RAM, 64 GB storage each): independent inference nodes using PrivateLM
- All devices communicate on a trusted private network. **RAM is not pooled into one 28 GB machine.**

## Project layout
- `gateway/app.py`: authenticated FastAPI router and phone failover
- `edge_clients/rejekt_ai_client.py`: optional Python backend client
- `tools/brand_phone_app.py`: label/prompt customization for pinned upstream PrivateLM source
- `.github/workflows/android-apk.yml`: GitHub Actions Android debug APK builder
- `Dockerfile`, `compose.yaml`, `requirements.txt`, `.env.example`: laptop deployment
- `tests/test_gateway.py`: gateway smoke tests

## Android build
Open **Actions → Build Device Mesh Android APK → Run workflow**. A successful workflow publishes the `device-mesh-android-debug` artifact containing `device-mesh-debug.apk`. The APK is a debug build, not a signed production release. Both phones can install the same APK.

The workflow checks out [PrivateLM](https://github.com/orailnoor/cross-platform-llm-client) at a pinned commit and applies limited branding; this repo does **not** contain or replace the upstream full Flutter source. Builds can fail if upstream native dependencies are incompatible. No APK is guaranteed until CI completes.

## Laptop gateway
1. Install Docker (Docker Desktop with WSL2 on Windows or Linux Docker).
2. Copy `.env.example` to `.env`, generate **three different strong secrets**, and set the two phones' LAN IP addresses.
3. On each phone load a supported small GGUF model, enable its local OpenAI-compatible server, require an API key, and note the URL.
4. Run `docker compose up -d --build` in this repository.
5. Smoke-test:

```sh
curl http://127.0.0.1:8787/health
curl -H 'Authorization: Bearer YOUR_EDGE_API_KEY' http://127.0.0.1:8787/v1/nodes
curl -X POST http://127.0.0.1:8787/v1/tasks -H 'Content-Type: application/json' -H 'Authorization: Bearer YOUR_EDGE_API_KEY' -d '{"task":"general","input":"Reply with hello"}'
```

## Scope & limitations
- Each phone executes one inference at a time. This gateway routes requests but does not distribute model layers between the laptop and phones.
- Upstream PrivateLM has experimental multi-phone clustering, which must be tested separately.
- Actual phone model compatibility, power, Wi-Fi latency, thermal throttling, and background process reliability remain unverified.
- Keep endpoints private, do not commit `.env`, and use a VPN if remote access is required.
- rejekt.ai is only an optional downstream client; no changes to its repository are necessary.
- Open source upstream: PrivateLM (MIT); see upstream license for its code.
