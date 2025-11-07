"""
統合テスト
収録→編集→出力の完全フローをテスト
"""
import pytest
from pathlib import Path
from PIL import Image
from utils.image_manager import ImageManager
from exporter.pptx_generator import PPTXGenerator


class TestIntegration:
    """統合テストクラス"""

    def test_basic_setup(self, temp_session_dir):
        """基本的なセットアップテスト"""
        assert temp_session_dir.exists()
        assert temp_session_dir.is_dir()
