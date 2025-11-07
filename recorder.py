#!/usr/bin/env python3
"""
Manual Maker - 収録モード
マウス・キーボード操作を検知してスクリーンショットを自動撮影
"""
import sys
import signal
from pathlib import Path
from datetime import datetime
import config
from utils.screenshot import ScreenshotCapture
from utils.event_detector import EventDetector
from utils.image_manager import ImageManager


class Recorder:
    """収録クラス"""

    def __init__(self):
        # セッションディレクトリの作成
        session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.session_dir = config.SESSIONS_DIR / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # コンポーネントの初期化
        self.screenshot = ScreenshotCapture(self.session_dir)
        self.image_manager = ImageManager(self.session_dir)
        self.event_detector = EventDetector(on_event=self._on_event)

        print(f"📁 Session directory: {self.session_dir}\n")

    def _on_event(self):
        """イベント発生時の処理（スクリーンショット撮影）"""
        filepath = self.screenshot.capture()
        self.image_manager.add_image(filepath)

    def start(self):
        """収録開始"""
        self.event_detector.start()

        try:
            # Ctrl+C が押されるまで待機
            self.event_detector.join()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """収録停止"""
        self.event_detector.stop()
        self.screenshot.close()
        print(f"\n✅ Recording completed!")
        print(f"   Screenshots saved: {len(self.image_manager.get_images())}")
        print(f"   Location: {self.session_dir}")
        print(f"\nNext step: Run 'streamlit run app.py' to edit and generate PowerPoint")


def main():
    """メイン処理"""
    recorder = Recorder()

    # Ctrl+C のシグナルハンドラ
    def signal_handler(sig, frame):
        recorder.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 収録開始
    recorder.start()


if __name__ == "__main__":
    main()
