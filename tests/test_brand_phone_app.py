import subprocess
import sys
from pathlib import Path


def test_branding_script_disables_android_vulkan(tmp_path):
    root = tmp_path / "private-lm"
    (root / "lib/views").mkdir(parents=True)
    (root / "lib/core").mkdir(parents=True)
    (root / "ios/Runner").mkdir(parents=True)
    (root / "local_plugins/llama_flutter_android/android").mkdir(parents=True)

    (root / "pubspec.yaml").write_text("name: private_lm\n")
    (root / "lib/views/server_view.dart").write_text(
        "appScreenBar(context, title: 'Server')\n"
        "const SectionHeader('Model')\n"
        "const SectionHeader('Endpoints')\n"
    )
    (root / "lib/core/constants.dart").write_text(
        "You are AI Chat, a helpful and friendly assistant.\n"
    )
    (root / "ios/Runner/Info.plist").write_text("<string>PrivateLM</string>\n")
    cmake_file = root / "local_plugins/llama_flutter_android/android/CMakeLists.txt"
    cmake_file.write_text(
        'option(LLAMA_ANDROID_VULKAN "Build the Vulkan GPU backend" ON)\n'
    )

    script = Path(__file__).resolve().parents[1] / "tools/brand_phone_app.py"
    subprocess.run([sys.executable, str(script), str(root)], check=True)

    assert (
        'option(LLAMA_ANDROID_VULKAN "Build the Vulkan GPU backend" OFF)'
        in cmake_file.read_text()
    )
