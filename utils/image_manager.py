"""
画像管理モジュール（編集・Undo機能）
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ImageData:
    """画像データクラス"""
    filepath: str
    description: str = ""
    order: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ImageManager:
    """画像管理クラス"""

    def __init__(self, session_dir: Path):
        """
        Args:
            session_dir: セッションディレクトリ
        """
        self.session_dir = session_dir
        self.metadata_file = session_dir / "metadata.json"
        self.images: List[ImageData] = []
        self.undo_stack: List[List[ImageData]] = []
        self._load_metadata()

    def _load_metadata(self):
        """メタデータの読み込み"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.images = [ImageData(**item) for item in data]
        else:
            # 既存の画像ファイルを自動検出
            self._auto_detect_images()

    def _auto_detect_images(self):
        """ディレクトリ内の画像を自動検出"""
        image_files = sorted(self.session_dir.glob("*.png"))
        for i, img_path in enumerate(image_files):
            self.images.append(ImageData(
                filepath=str(img_path),
                order=i
            ))

    def save_metadata(self):
        """メタデータの保存"""
        data = [asdict(img) for img in self.images]
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_state(self):
        """現在の状態をUndo スタックに保存"""
        import copy
        self.undo_stack.append(copy.deepcopy(self.images))
        # スタックが大きくなりすぎないよう制限
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def add_image(self, filepath: Path) -> ImageData:
        """
        画像を追加

        Args:
            filepath: 画像ファイルパス

        Returns:
            追加された画像データ
        """
        self._save_state()
        img_data = ImageData(
            filepath=str(filepath),
            order=len(self.images)
        )
        self.images.append(img_data)
        self.save_metadata()
        return img_data

    def update_description(self, index: int, description: str):
        """
        説明文を更新

        Args:
            index: 画像インデックス
            description: 説明文
        """
        if 0 <= index < len(self.images):
            self._save_state()
            self.images[index].description = description
            self.save_metadata()

    def delete_image(self, index: int):
        """
        画像を削除

        Args:
            index: 画像インデックス
        """
        if 0 <= index < len(self.images):
            self._save_state()
            self.images.pop(index)
            # orderを再割り当て
            for i, img in enumerate(self.images):
                img.order = i
            self.save_metadata()

    def reorder_images(self, new_order: List[int]):
        """
        画像の順序を変更

        Args:
            new_order: 新しい順序のインデックスリスト
        """
        self._save_state()
        self.images = [self.images[i] for i in new_order]
        for i, img in enumerate(self.images):
            img.order = i
        self.save_metadata()

    def swap_images(self, idx1: int, idx2: int):
        """
        2つの画像の順序を入れ替え

        Args:
            idx1: 1つ目の画像インデックス
            idx2: 2つ目の画像インデックス
        """
        if 0 <= idx1 < len(self.images) and 0 <= idx2 < len(self.images):
            current_order = list(range(len(self.images)))
            current_order[idx1], current_order[idx2] = current_order[idx2], current_order[idx1]
            self.reorder_images(current_order)

    def undo(self) -> bool:
        """
        直前の操作を取り消し

        Returns:
            Undo成功の場合True
        """
        if self.undo_stack:
            self.images = self.undo_stack.pop()
            self.save_metadata()
            return True
        return False

    def get_images(self) -> List[ImageData]:
        """
        画像リストを取得

        Returns:
            画像データのリスト
        """
        return self.images
