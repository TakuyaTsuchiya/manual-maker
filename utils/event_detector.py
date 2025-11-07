"""
マウス・キーボードイベント検知モジュール
"""
import time
from pynput import mouse, keyboard
from typing import Callable
import config


class EventDetector:
    """マウス・キーボードイベント検知クラス"""

    def __init__(self, on_event: Callable):
        """
        Args:
            on_event: イベント発生時に呼び出すコールバック関数
        """
        self.on_event = on_event
        self.last_event_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None

    def _should_trigger(self) -> bool:
        """
        デバウンス処理（連続イベントを防ぐ）

        Returns:
            イベントを発火すべきかどうか
        """
        current_time = time.time()
        if current_time - self.last_event_time >= config.DEBOUNCE_TIME:
            self.last_event_time = current_time
            return True
        return False

    def _on_click(self, x, y, button, pressed):
        """マウスクリック時のハンドラ"""
        if pressed and config.DETECT_MOUSE_CLICK and self._should_trigger():
            print(f"🖱️  Mouse click detected at ({x}, {y})")
            self.on_event()

    def _on_key_press(self, key):
        """キー押下時のハンドラ"""
        if config.DETECT_KEY_PRESS and self._should_trigger():
            try:
                key_name = key.char if hasattr(key, 'char') else str(key)
                print(f"⌨️  Key press detected: {key_name}")
                self.on_event()
            except AttributeError:
                pass

    def start(self):
        """イベント検知開始"""
        print("🎬 Recording started. Press Ctrl+C to stop.")
        print(f"   - Mouse click detection: {config.DETECT_MOUSE_CLICK}")
        print(f"   - Key press detection: {config.DETECT_KEY_PRESS}")
        print(f"   - Debounce time: {config.DEBOUNCE_TIME}s\n")

        # マウスリスナー
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.mouse_listener.start()

        # キーボードリスナー
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()

    def stop(self):
        """イベント検知停止"""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        print("\n🛑 Recording stopped.")

    def join(self):
        """リスナーの終了を待機"""
        if self.mouse_listener:
            self.mouse_listener.join()
        if self.keyboard_listener:
            self.keyboard_listener.join()
