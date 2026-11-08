# Device Mesh roadmap

## Implemented source
- Android Flutter wrapper build workflow (debug APK, upstream pinned)
- iOS Flutter wrapper build workflow (unsigned IPA, upstream pinned)
- Authenticated FastAPI mixed-platform node routing
- Docker-based Windows/Linux laptop coordinator
- Optional backend client for rejekt.ai with no modifications to its repository

## Test before relying on it
- Verify Android APK CI compilation and two physical-phone installs
- Verify IPA CI compilation, sideload signing, iOS local-network authorization, and real iPhone inference
- Benchmark accuracy and tokens/s on each device, error handling, concurrency, heat, Wi-Fi dropouts, and power use
- Validate current upstream code and dependencies for security and distribution

## Next steps
- Pairing QR codes and secure first-time enrollment; revoke device credentials
- Device heartbeat, capability reporting, dynamic scheduling by model/VRAM/RAM
- Queue persistent tasks and reconnect safely after suspension
- Windows desktop tray node installer and model runtime launcher
- MacBook macOS native menu-bar node with Apple Silicon Metal acceleration
- Opt-in automatic model downloads and versioned node updates
- Signed Android release and properly signed iOS distribution if Apple developer credentials become available

**Design rule:** keep the coordinator's wire format OpenAI-compatible so new platforms can register as nodes without rewriting rejekt.ai or other calling applications.
