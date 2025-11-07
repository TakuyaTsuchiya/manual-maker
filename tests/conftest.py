"""
pytest共通設定とフィクスチャ
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from utils.image_manager import ImageData


@pytest.fixture
def temp_session_dir():
    """
    一時セッションディレクトリを作成

    Yields:
        Path: 一時ディレクトリのパス（テスト後自動削除）
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="test_session_"))
    yield temp_dir
    # テスト終了後にクリーンアップ
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_images(temp_session_dir):
    """
    テスト用のサンプル画像を作成

    Args:
        temp_session_dir: 一時セッションディレクトリ

    Returns:
        List[Path]: 作成した画像ファイルのパスリスト
    """
    image_paths = []
    for i in range(3):
        # 100x100のテスト画像を作成
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        filepath = temp_session_dir / f"test_{i:04d}.png"
        img.save(filepath)
        image_paths.append(filepath)
    return image_paths


@pytest.fixture
def sample_image_data(sample_images):
    """
    テスト用のImageDataリストを作成

    Args:
        sample_images: サンプル画像パスリスト

    Returns:
        List[ImageData]: ImageDataのリスト
    """
    return [
        ImageData(
            filepath=str(img_path),
            description=f"Test image {i}",
            order=i
        )
        for i, img_path in enumerate(sample_images)
    ]


@pytest.fixture
def mock_screenshot(mocker):
    """
    スクリーンショットのモック

    Args:
        mocker: pytest-mockのmocker

    Returns:
        Mock: mss.mss()のモックオブジェクト
    """
    mock_sct = mocker.MagicMock()

    # モニタ情報のモック
    mock_sct.monitors = [
        {'left': 0, 'top': 0, 'width': 1920, 'height': 1080},
        {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}
    ]

    # grab()のモック（100x100のダミー画像データ）
    mock_screenshot_data = mocker.MagicMock()
    mock_screenshot_data.size = (100, 100)
    mock_screenshot_data.bgra = b'\x00' * (100 * 100 * 4)
    mock_sct.grab.return_value = mock_screenshot_data

    return mock_sct
