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

    def test_session_load_and_save(self, temp_session_dir, sample_images):
        """セッションの読み込みと保存テスト"""
        # 初回ロード - 画像を自動検出
        manager1 = ImageManager(temp_session_dir)
        assert len(manager1.images) == 3

        # 説明文を追加
        manager1.update_description(0, "Test description 1")
        manager1.update_description(1, "Test description 2")
        manager1.save_metadata()

        # 新しいインスタンスでロード - 保存した説明文が読み込まれるか
        manager2 = ImageManager(temp_session_dir)
        assert len(manager2.images) == 3
        assert manager2.images[0].description == "Test description 1"
        assert manager2.images[1].description == "Test description 2"
        assert manager2.images[2].description == ""  # Empty string, not None

    def test_session_metadata_persistence(self, temp_session_dir, sample_images):
        """メタデータ永続化の詳細テスト"""
        manager = ImageManager(temp_session_dir)

        # 複数の操作を実行
        manager.update_description(0, "First")
        manager.update_description(1, "Second")
        manager.update_description(2, "Third")
        manager.save_metadata()

        # metadata.jsonが存在するか
        metadata_file = temp_session_dir / "metadata.json"
        assert metadata_file.exists()

        # 新しいマネージャーで読み込み
        new_manager = ImageManager(temp_session_dir)
        assert new_manager.images[0].description == "First"
        assert new_manager.images[1].description == "Second"
        assert new_manager.images[2].description == "Third"

        # 順序も保持されているか
        for i, img in enumerate(new_manager.images):
            assert img.order == i

    def test_multiple_undo_redo(self, temp_session_dir, sample_images):
        """複数回のUndo/Redoテスト"""
        manager = ImageManager(temp_session_dir)
        initial_count = len(manager.images)

        # 操作1: 説明文更新
        manager.update_description(0, "Step 1")
        assert manager.images[0].description == "Step 1"
        assert len(manager.undo_stack) == 1

        # 操作2: 説明文更新
        manager.update_description(1, "Step 2")
        assert manager.images[1].description == "Step 2"
        assert len(manager.undo_stack) == 2

        # 操作3: 削除
        manager.delete_image(2)
        assert len(manager.images) == initial_count - 1
        assert len(manager.undo_stack) == 3

        # Undo 1回目: 削除を取り消し
        assert manager.undo() is True
        assert len(manager.images) == initial_count
        assert len(manager.undo_stack) == 2

        # Undo 2回目: Step 2を取り消し
        assert manager.undo() is True
        assert manager.images[1].description == ""
        assert len(manager.undo_stack) == 1

        # Undo 3回目: Step 1を取り消し
        assert manager.undo() is True
        assert manager.images[0].description == ""
        assert len(manager.undo_stack) == 0

        # もうUndoできない
        assert manager.undo() is False

    def test_undo_preserves_order(self, temp_session_dir, sample_images):
        """Undoが順序を正しく復元するかテスト"""
        manager = ImageManager(temp_session_dir)

        # 元の順序を記録
        original_paths = [img.filepath for img in manager.images]

        # 並び替え
        manager.swap_images(0, 2)
        reordered_paths = [img.filepath for img in manager.images]

        # 順序が変わっているか
        assert reordered_paths != original_paths
        assert reordered_paths == [original_paths[2], original_paths[1], original_paths[0]]

        # Undo
        manager.undo()
        restored_paths = [img.filepath for img in manager.images]

        # 元の順序に戻っているか
        assert restored_paths == original_paths
