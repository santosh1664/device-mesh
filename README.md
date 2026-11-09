# Device Mesh AI

A standalone **local AI network** connecting Android phones to a Windows/Linux laptop coordinator. iPhone and MacBook support are postponed for a future release. This project is independent of rejekt.ai; the optional client adapter lives in `edge_clients/`.

## Download Android app

**Latest published preview:** [Device Mesh AI v0.1.0-preview.1](https://github.com/santosh1664/device-mesh/releases/tag/v0.1.0-preview.1)

| Platform | Direct download | Installation notes |
|---|---|---|
| **Android** | [Download Android APK](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-debug.apk) | Debug build; install on a compatible Android device. Vulkan GPU acceleration is disabled in this build. |

[Browse all releases](https://github.com/santosh1664/device-mesh/releases) · [Android SHA-256 checksum](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-android-SHA256SUMS.txt)

This is a **developer preview build**. GitHub Actions compilation succeeded, but installation and local inference on physical Android devices have not yet been verified.

## Platform support

| Platform | Current integration | Build/distribution |
|---|---|---|
| Android | PrivateLM-backed inference node | `device-mesh-android-debug` APK, GitHub Actions |
| iOS / iPadOS | Postponed | No iOS build or download in current releases |
| Windows | Docker/Python coordinator; optional OpenAI-compatible model endpoint | Docker Compose; no Windows installer |
| macOS | Planned node integration (generic OpenAI-compatible endpoint can be configured already) | Native Mac application not yet implemented |

See [platform installation instructions](docs/platforms.md) and [roadmap](docs/roadmap.md).

## Network layout

```
             Your application (optional rejekt.ai adapter)
                               |
                   Windows/Linux coordinator
                       FastAPI :8787
                               |
                Authenticated private LAN/VPN
                  /       |         \
             Android    Android     Windows model server
             PrivateLM   PrivateLM  (optional)
```

This gateway routes **independent inference requests**, not shared RAM or combined GPU memory. Devices retain their own hardware limits. In future, macOS can serve as an additional node through the same protocol.

## Install and configure the coordinator

1. Install Docker Desktop + WSL2 on Windows (or Docker on Linux).
2. Copy `.env.example` to `.env`.
3. Generate a long independent API token for the gateway and each device. Enter real device LAN IPs.
4. Start the coordinator using `docker compose up -d --build`.
5. On each device open its model server, load a compatible model and enable authenticated network access.
6. Test:

```sh
curl http://127.0.0.1:8787/health
curl -H 'Authorization: Bearer YOUR_EDGE_API_KEY' http://127.0.0.1:8787/v1/nodes
curl -X POST http://127.0.0.1:8787/v1/tasks -H 'Content-Type: application/json' -H 'Authorization: Bearer YOUR_EDGE_API_KEY' -d '{"task":"general","input":"Reply with hello"}'
```

## Build Android APK

On the repository's **Actions** tab:
- **Build Device Mesh Android APK** produces a debug APK from pinned PrivateLM source when successful.

The Android workflow applies small branding changes while retaining PrivateLM's inference engine. Real-device compatibility still requires testing. **iOS work is on hold.**

## Security and limitations

- Keep `.env` private, never put coordinator credentials in browser code or public GitHub files.
- Enable unique node tokens; expose servers only to your private network or VPN.
- Phones may suspend inference in the background or overheat under prolonged load.
- The gateway is experimental, not a production-grade persistent job queue.
- Upstream PrivateLM: https://github.com/orailnoor/cross-platform-llm-client (MIT). Verify license and native dependencies for redistribution.
