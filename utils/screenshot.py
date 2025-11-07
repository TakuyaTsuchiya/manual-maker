"""
スクリーンショット撮影モジュール
"""
import mss
from PIL import Image
from pathlib import Path
from datetime import datetime
import config


class ScreenshotCapture:
    """スクリーンショット撮影クラス"""

    def __init__(self, session_dir: Path):
        """
        Args:
            session_dir: セッション保存先ディレクトリ
        """
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.counter = 0
        self.sct = mss.mss()

    def capture(self) -> Path:
        """
        画面全体のスクリーンショットを撮影

        Returns:
            保存したファイルのパス
        """
        # タイムスタンプ付きファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.counter:04d}_{timestamp}.{config.SCREENSHOT_FORMAT}"
        filepath = self.session_dir / filename

        # スクリーンショット撮影（全モニタ）
        screenshot = self.sct.grab(self.sct.monitors[0])

        # PIL Imageに変換して保存
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(filepath, quality=config.SCREENSHOT_QUALITY)

        self.counter += 1
        print(f"📸 Screenshot saved: {filepath.name}")

        return filepath

    def close(self):
        """リソースの解放"""
        self.sct.close()
