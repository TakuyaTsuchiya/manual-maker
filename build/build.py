"""
ビルドスクリプト
PyInstallerを使用してWindows/macOS用の実行ファイルを生成
"""
import sys
import platform
import subprocess
from pathlib import Path


def get_platform():
    """現在のプラットフォームを取得"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def build_recorder(output_dir: Path):
    """
    Recorder用の実行ファイルをビルド

    Args:
        output_dir: 出力ディレクトリ
    """
    print("=" * 60)
    print("Recorderをビルドしています...")
    print("=" * 60)

    current_platform = get_platform()

    cmd = [
        "pyinstaller",
        "--name=recorder",
        "--onefile",
        "--windowed" if current_platform == "macos" else "--console",
        "--add-data=config.py:.",
        f"--distpath={output_dir}",
        "recorder.py"
    ]

    print(f"コマンド: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("✅ Recorderのビルド完了")


def build_app(output_dir: Path):
    """
    Streamlit App用の実行ファイルをビルド

    Args:
        output_dir: 出力ディレクトリ
    """
    print("=" * 60)
    print("Streamlit Appをビルドしています...")
    print("=" * 60)

    current_platform = get_platform()

    cmd = [
        "pyinstaller",
        "--name=manual-maker-app",
        "--onefile",
        "--windowed" if current_platform == "macos" else "--console",
        "--add-data=config.py:.",
        "--hidden-import=streamlit",
        "--hidden-import=utils.image_manager",
        "--hidden-import=exporter.pptx_generator",
        f"--distpath={output_dir}",
        "app.py"
    ]

    print(f"コマンド: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("✅ Streamlit Appのビルド完了")


def build_windows():
    """Windows版をビルド"""
    print("\n🪟 Windows版をビルドします\n")
    output_dir = Path("dist/windows")
    output_dir.mkdir(parents=True, exist_ok=True)

    build_recorder(output_dir)
    build_app(output_dir)

    print("\n" + "=" * 60)
    print("✅ Windows版のビルド完了")
    print(f"出力ディレクトリ: {output_dir.absolute()}")
    print("=" * 60)


def build_macos():
    """macOS版をビルド"""
    print("\n🍎 macOS版をビルドします\n")
    output_dir = Path("dist/macos")
    output_dir.mkdir(parents=True, exist_ok=True)

    build_recorder(output_dir)
    build_app(output_dir)

    print("\n" + "=" * 60)
    print("✅ macOS版のビルド完了")
    print(f"出力ディレクトリ: {output_dir.absolute()}")
    print("=" * 60)


def main():
    """メイン関数"""
    print("=" * 60)
    print("Manual Maker - ビルドスクリプト")
    print("=" * 60)

    current_platform = get_platform()
    print(f"現在のプラットフォーム: {current_platform}\n")

    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "windows":
            build_windows()
        elif target == "macos":
            build_macos()
        else:
            print(f"❌ 不明なターゲット: {target}")
            print("使い方: python build.py [windows|macos]")
            sys.exit(1)
    else:
        # プラットフォーム自動検出
        if current_platform == "windows":
            build_windows()
        elif current_platform == "macos":
            build_macos()
        else:
            print("❌ このプラットフォームはサポートされていません")
            print("手動で指定してください: python build.py [windows|macos]")
            sys.exit(1)


if __name__ == "__main__":
    main()
