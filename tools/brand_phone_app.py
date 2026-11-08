"""Safe, minimal branding patch for pinned PrivateLM Android and iOS builds."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    sys.exit("Usage: python3 tools/brand_phone_app.py /path/to/private-lm")
root = Path(sys.argv[1]).expanduser()
if not (root / "pubspec.yaml").is_file():
    sys.exit("PrivateLM source missing: pubspec.yaml")

replacements = {
    "lib/views/server_view.dart": [
        ("appScreenBar(context, title: 'Server')", "appScreenBar(context, title: 'Device Mesh AI Node')"),
        ("const SectionHeader('Model')", "const SectionHeader('AI Model')"),
        ("const SectionHeader('Endpoints')", "const SectionHeader('Device Mesh Endpoints')"),
    ],
    "lib/core/constants.dart": [
        ("You are AI Chat, a helpful and friendly assistant.", "You are a helpful assistant for connected applications."),
    ],
    "ios/Runner/Info.plist": [
        ("<string>PrivateLM</string>", "<string>Device Mesh AI</string>"),
    ],
}

for filename, changes in replacements.items():
    path = root / filename
    if not path.is_file():
        sys.exit(f"Expected upstream file missing: {filename}")
    original = path.read_text()
    updated = original
    for before, after in changes:
        if before not in updated and after not in updated:
            sys.exit(f"Unexpected upstream structure: {filename}: {before}")
        updated = updated.replace(before, after)
    if updated != original:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original)
        path.write_text(updated)
    print("Ready:", filename)

print("Branding applied; validate build and device-specific inference support.")
