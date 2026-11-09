# Device Mesh AI

A standalone **mixed-device local AI network** that connects Android phones, iPhones/iPads, and Windows laptops, with an extensible interface for a future MacBook node. This project is independent of rejekt.ai; the optional client adapter lives in `edge_clients/`.

## Download mobile apps

**Latest published preview:** [Device Mesh AI v0.1.0-preview.1](https://github.com/santosh1664/device-mesh/releases/tag/v0.1.0-preview.1)

| Platform | Direct download | Installation notes |
|---|---|---|
| **Android** | [Download Android APK](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-debug.apk) | Debug build; install on a compatible Android device. Vulkan GPU acceleration is disabled in this build. |
| **iPhone / iPad** | [Download iOS IPA (unsigned)](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-ios-unsigned.ipa) | Requires Apple-compatible signing and provisioning; **cannot be installed directly** like an APK. |

[Browse all releases](https://github.com/santosh1664/device-mesh/releases) · [Android SHA-256 checksum](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-android-SHA256SUMS.txt) · [iOS SHA-256 checksum](https://github.com/santosh1664/device-mesh/releases/download/v0.1.0-preview.1/device-mesh-ios-SHA256SUMS.txt)

These are **developer preview builds**. GitHub Actions compilation succeeded, but installation and local inference on physical devices have not yet been verified.

## Platform support

| Platform | Current integration | Build/distribution |
|---|---|---|
| Android | PrivateLM-backed inference node | `device-mesh-android-debug` APK, GitHub Actions |
| iOS / iPadOS | Experimental PrivateLM-backed inference node | `device-mesh-ios-unsigned-ipa`; **must be signed before installation** |
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
             Android    iPhone     PC/Mac model server
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

## Build mobile apps

On the repository's **Actions** tab:
- **Build Device Mesh Android APK** produces a debug APK from pinned PrivateLM source when successful.
- **Build Device Mesh iPhone IPA (unsigned)** attempts to build an iOS app on macOS and packages an unsigned IPA. You cannot simply install that IPA like an Android APK. Use an Apple-supported signing route or AltStore, and test it on a real iPhone. Requires iOS 16.2 or newer per upstream project.

Both workflows apply small branding changes while retaining PrivateLM's inference engine. APK/IPA builds and mobile compatibility are **not guaranteed until the Actions workflows and device tests succeed**.

## Security and limitations

- Keep `.env` private, never put coordinator credentials in browser code or public GitHub files.
- Enable unique node tokens; expose servers only to your private network or VPN.
- Phones may suspend inference in the background or overheat under prolonged load.
- The gateway is experimental, not a production-grade persistent job queue.
- Upstream PrivateLM: https://github.com/orailnoor/cross-platform-llm-client (MIT). Verify license and native dependencies for redistribution.
