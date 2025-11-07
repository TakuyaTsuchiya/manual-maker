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


@pytest.mark.skip(reason="Requires pytest-mock to be installed")
def test_mock_screenshot_fixture(mock_screenshot):
    """mock_screenshotフィクスチャのテスト (requires pytest-mock)"""
    # モニタ情報が正しくモックされているか
    assert len(mock_screenshot.monitors) == 2
    assert mock_screenshot.monitors[1]['width'] == 1920
    assert mock_screenshot.monitors[1]['height'] == 1080

    # grab()メソッドがモックされているか
    screenshot = mock_screenshot.grab(mock_screenshot.monitors[0])
    assert screenshot is not None
    assert screenshot.size == (100, 100)
    assert len(screenshot.bgra) == 100 * 100 * 4
