# Device Mesh — platform and installation matrix

| Device | Role now | Artifact | Inference backend | Notes |
|---|---|---|---|---|
| Android phone | Local AI node | Debug APK from Actions | PrivateLM llama.cpp | Android 9+ is the upstream documented minimum; verify model/GPU compatibility |
| iPhone / iPad | Local AI node (experimental) | **Unsigned IPA** from Actions | PrivateLM iOS | Upstream minimum iOS 16.2; requires signing through AltStore or Apple developer tools, test on a real device |
| Windows laptop | Coordinator + optional inference node | Python + Docker Compose | Gateway; optional authenticated llama.cpp server | 12 GB RAM limits local model size and concurrency |
| MacBook | Future inference node | Not built yet | Planned llama.cpp/Ollama-style adapter | macOS agent, lifecycle management, and packaging are future work |

## Install Android
1. Open the Actions tab, choose **Build Device Mesh Android APK**, and run it.
2. Download `device-mesh-android-debug` from a **successful** run, extract APK.
3. Install on your trusted Android device.
4. Load a small GGUF model, enable PrivateLM Server with a unique key, and allow LAN access.

## Install iPhone / iPad
1. Open Actions, choose **Build Device Mesh iPhone IPA (unsigned)**, and run it.
2. A successful build has artifact `device-mesh-ios-unsigned-ipa` containing `device-mesh-ios-unsigned.ipa`.
3. The IPA is **not installable directly** because it is unsigned. Sign/sideload using AltStore/AltServer (or sign with your Apple developer provisioning profile in Xcode), subject to Apple's rules and device compatibility.
4. Enable Local Network permission in iOS Settings if prompted. Open Device Mesh AI, load a supported model, and enable its authenticated LAN server.

Unsigned packaging is not proof that AltStore successfully signs/installs the build. Native plugin dependency issues or entitlement/signing failures may prevent it. Real device tests are required. Apple ID based sideloaded apps may need periodic re-signing (often every 7 days for free provisioning).

## Register nodes on the coordinator
Copy `.env.example` to `.env`. Each `NODE_N_PLATFORM` is one of `android, ios, windows, macos, linux`. Configure its URL and *its own* token. `NODE_N_URL` must be accessible **from the gateway's Docker container**, not just from a browser on the host. Restart Docker Compose after changing the environment.

For older configurations, `PHONE_1_URL/KEY` and `PHONE_2_URL/KEY` remain compatible.

## Cluster behavior
The gateway does **request routing**: each device independently executes one request. It does not pool system RAM, combine GPU memory, or transparently split a single model across different operating systems.

The upstream PrivateLM experimental Android-led **phone layer clustering** is a separate feature, requiring device compatibility and benchmarks. The Windows and macOS backends are not part of that model-layer cluster.

## Operating safeguards
Keep API tokens out of Git and mobile/web frontends. Use a VPN to connect nodes over untrusted networks. Avoid publicly exposing model servers or the coordinator. Devices can sleep, disconnect, throttle, or become unavailable: production jobs need queueing, retry limits, and a cloud fallback.
