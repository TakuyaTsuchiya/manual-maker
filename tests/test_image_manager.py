"""
ImageManagerのテスト
"""
import pytest
import json
from pathlib import Path
from utils.image_manager import ImageManager, ImageData


class TestImageManager:
    """ImageManagerクラスのテスト"""

    def test_init_empty_session(self, temp_session_dir):
        """空のセッションでの初期化"""
        manager = ImageManager(temp_session_dir)
        assert manager.session_dir == temp_session_dir
        assert len(manager.images) == 0
        assert len(manager.undo_stack) == 0

    def test_init_with_existing_images(self, temp_session_dir, sample_images):
        """既存の画像がある場合の自動検出"""
        manager = ImageManager(temp_session_dir)
        assert len(manager.images) == 3
        for i, img_data in enumerate(manager.images):
            assert Path(img_data.filepath).exists()
            assert img_data.order == i

    def test_add_image(self, temp_session_dir, sample_images):
        """画像追加のテスト"""
        manager = ImageManager(temp_session_dir)
        initial_count = len(manager.images)

        # 新しい画像を追加
        from PIL import Image
        new_img_path = temp_session_dir / "new_image.png"
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img.save(new_img_path)

        img_data = manager.add_image(new_img_path)

        # 検証
        assert len(manager.images) == initial_count + 1
        assert img_data.filepath == str(new_img_path)
        assert img_data.order == initial_count
        assert len(manager.undo_stack) == 1  # Undo用に状態保存

        # metadata.jsonが保存されているか
        assert manager.metadata_file.exists()

    def test_update_description(self, temp_session_dir, sample_images):
        """説明文更新のテスト"""
        manager = ImageManager(temp_session_dir)

        # 説明文を更新
        manager.update_description(0, "Updated description")

        # 検証
        assert manager.images[0].description == "Updated description"
        assert len(manager.undo_stack) == 1

    def test_update_description_invalid_index(self, temp_session_dir, sample_images):
        """不正なインデックスでの説明文更新"""
        manager = ImageManager(temp_session_dir)
        initial_stack_size = len(manager.undo_stack)

        # 範囲外のインデックス
        manager.update_description(999, "Should not update")

        # 何も変更されない
        assert len(manager.undo_stack) == initial_stack_size

    def test_delete_image(self, temp_session_dir, sample_images):
        """画像削除のテスト"""
        manager = ImageManager(temp_session_dir)
        initial_count = len(manager.images)

        # 最初の画像を削除
        manager.delete_image(0)

        # 検証
        assert len(manager.images) == initial_count - 1
        assert len(manager.undo_stack) == 1

        # orderが再割り当てされているか
        for i, img_data in enumerate(manager.images):
            assert img_data.order == i

    def test_delete_image_invalid_index(self, temp_session_dir, sample_images):
        """不正なインデックスでの削除"""
        manager = ImageManager(temp_session_dir)
        initial_count = len(manager.images)
        initial_stack_size = len(manager.undo_stack)

        # 範囲外のインデックス
        manager.delete_image(999)

        # 何も変更されない
        assert len(manager.images) == initial_count
        assert len(manager.undo_stack) == initial_stack_size

    def test_reorder_images(self, temp_session_dir, sample_images):
        """画像順序変更のテスト"""
        manager = ImageManager(temp_session_dir)

        # 元の順序を記録
        original_paths = [img.filepath for img in manager.images]

        # 順序を逆転
        new_order = [2, 1, 0]
        manager.reorder_images(new_order)

        # 検証
        reordered_paths = [img.filepath for img in manager.images]
        assert reordered_paths == [original_paths[2], original_paths[1], original_paths[0]]

        # orderが正しく設定されているか
        for i, img_data in enumerate(manager.images):
            assert img_data.order == i

        assert len(manager.undo_stack) == 1

    def test_undo(self, temp_session_dir, sample_images):
        """Undo機能のテスト"""
        manager = ImageManager(temp_session_dir)

        # 初期状態を記録
        initial_count = len(manager.images)

        # 画像を追加
        from PIL import Image
        new_img_path = temp_session_dir / "new_image.png"
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        img.save(new_img_path)
        manager.add_image(new_img_path)

        assert len(manager.images) == initial_count + 1

        # Undo実行
        result = manager.undo()

        # 検証
        assert result is True
        assert len(manager.images) == initial_count
        assert len(manager.undo_stack) == 0

    def test_undo_empty_stack(self, temp_session_dir):
        """Undoスタックが空の時のテスト"""
        manager = ImageManager(temp_session_dir)

        # Undoスタックが空
        result = manager.undo()

        # 失敗
        assert result is False

    def test_save_and_load_metadata(self, temp_session_dir, sample_images):
        """メタデータの保存と読み込みのテスト"""
        # 保存
        manager1 = ImageManager(temp_session_dir)
        manager1.update_description(0, "Test description")
        manager1.save_metadata()

        # 新しいインスタンスで読み込み
        manager2 = ImageManager(temp_session_dir)

        # 検証
        assert len(manager2.images) == len(manager1.images)
        assert manager2.images[0].description == "Test description"
        assert manager2.images[0].filepath == manager1.images[0].filepath

    def test_metadata_file_format(self, temp_session_dir, sample_images):
        """metadata.jsonのフォーマット検証"""
        manager = ImageManager(temp_session_dir)
        manager.update_description(0, "Test")
        manager.save_metadata()

        # JSONファイルを直接読み込み
        with open(manager.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # フォーマット検証
        assert isinstance(data, list)
        assert len(data) == 3
        assert 'filepath' in data[0]
        assert 'description' in data[0]
        assert 'order' in data[0]
        assert 'timestamp' in data[0]

    def test_auto_detect_images(self, temp_session_dir):
        """画像自動検出のテスト"""
        # metadata.jsonがない状態で画像ファイルを作成
        from PIL import Image
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            filepath = temp_session_dir / f"image_{i:04d}.png"
            img.save(filepath)

        # ImageManagerを初期化（自動検出される）
        manager = ImageManager(temp_session_dir)

        # 検証
        assert len(manager.images) == 3
        for i, img_data in enumerate(manager.images):
            assert Path(img_data.filepath).exists()
            assert img_data.filepath.endswith('.png')

    def test_undo_stack_limit(self, temp_session_dir, sample_images):
        """Undoスタックの上限テスト（50件）"""
        manager = ImageManager(temp_session_dir)

        # 60回の操作を実行
        for i in range(60):
            manager.update_description(0, f"Description {i}")

        # スタックは50件に制限される
        assert len(manager.undo_stack) <= 50

    def test_get_images(self, temp_session_dir, sample_images):
        """get_images()のテスト"""
        manager = ImageManager(temp_session_dir)

        images = manager.get_images()

        assert isinstance(images, list)
        assert len(images) == 3
        assert all(isinstance(img, ImageData) for img in images)

    def test_multiple_operations_with_undo(self, temp_session_dir, sample_images):
        """複数操作とUndoの統合テスト"""
        manager = ImageManager(temp_session_dir)

        # 操作1: 説明文更新
        manager.update_description(0, "First update")
        state1_desc = manager.images[0].description

        # 操作2: 削除
        manager.delete_image(2)
        state2_count = len(manager.images)

        # Undo1回目: 削除を取り消し
        manager.undo()
        assert len(manager.images) == 3

        # Undo2回目: 説明文更新を取り消し
        manager.undo()
        assert manager.images[0].description != state1_desc
