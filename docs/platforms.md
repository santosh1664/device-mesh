# Device Mesh — platform and installation matrix

| Device | Role now | Artifact | Inference backend | Notes |
|---|---|---|---|---|
| Android phone | Local AI node | Debug APK from Actions | PrivateLM llama.cpp | Android 9+ is the upstream documented minimum; verify model/GPU compatibility |
| iPhone / iPad | Postponed | None currently published | Future iOS node | iOS signing and distribution will be revisited later |
| Windows laptop | Coordinator + optional inference node | Python + Docker Compose | Gateway; optional authenticated llama.cpp server | 12 GB RAM limits local model size and concurrency |
| MacBook | Future inference node | Not built yet | Planned llama.cpp/Ollama-style adapter | macOS agent, lifecycle management, and packaging are future work |

## Install Android
1. Open the Actions tab, choose **Build Device Mesh Android APK**, and run it.
2. Download `device-mesh-android-debug` from a **successful** run, extract APK.
3. Install on your trusted Android device.
4. Load a small GGUF model, enable PrivateLM Server with a unique key, and allow LAN access.

## iPhone / iPad — postponed
There is no iOS workflow or supported download in the current Android-focused releases. Signing, device enrollment and installation will be revisited later.

## Register nodes on the coordinator
Copy `.env.example` to `.env`. Use `android` and optionally `windows` or `linux` nodes for now. The coordinator protocol retains `ios` and `macos` identifiers for future implementation. Configure its URL and *its own* token. `NODE_N_URL` must be accessible **from the gateway's Docker container**, not just from a browser on the host. Restart Docker Compose after changing the environment.

For older configurations, `PHONE_1_URL/KEY` and `PHONE_2_URL/KEY` remain compatible.

## Cluster behavior
The gateway does **request routing**: each device independently executes one request. It does not pool system RAM, combine GPU memory, or transparently split a single model across different operating systems.

The upstream PrivateLM experimental Android-led **phone layer clustering** is a separate feature, requiring device compatibility and benchmarks. The Windows and macOS backends are not part of that model-layer cluster.

## Operating safeguards
Keep API tokens out of Git and mobile/web frontends. Use a VPN to connect nodes over untrusted networks. Avoid publicly exposing model servers or the coordinator. Devices can sleep, disconnect, throttle, or become unavailable: production jobs need queueing, retry limits, and a cloud fallback.
