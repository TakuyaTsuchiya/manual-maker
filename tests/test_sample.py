"""
サンプルテスト（pytest動作確認用）
"""
import pytest


def test_sample():
    """基本的なテスト"""
    assert 1 + 1 == 2


def test_with_temp_dir(temp_session_dir):
    """temp_session_dirフィクスチャのテスト"""
    assert temp_session_dir.exists()
    assert temp_session_dir.is_dir()


def test_with_sample_images(sample_images):
    """sample_imagesフィクスチャのテスト"""
    assert len(sample_images) == 3
    for img_path in sample_images:
        assert img_path.exists()
        assert img_path.suffix == '.png'
