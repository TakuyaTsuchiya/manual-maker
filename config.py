"""
設定管理モジュール
"""
import os
from pathlib import Path

# プロジェクトルート
BASE_DIR = Path(__file__).parent

# データ保存先
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"

# スクリーンショット設定
SCREENSHOT_FORMAT = "png"
SCREENSHOT_QUALITY = 95

# 収録設定
DETECT_MOUSE_CLICK = True
DETECT_KEY_PRESS = True
DEBOUNCE_TIME = 0.5  # 連続操作の検知間隔（秒）

# PowerPoint設定
PPTX_SLIDE_WIDTH = 10  # インチ
PPTX_SLIDE_HEIGHT = 7.5  # インチ
PPTX_IMAGE_WIDTH_RATIO = 0.8  # スライド幅に対する画像の比率

# ディレクトリの自動作成
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
