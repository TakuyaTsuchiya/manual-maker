# Manual Maker - 設計書

## 1. システムアーキテクチャ

### 1.1 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │   CLI (Recorder)  │      │  Streamlit UI    │        │
│  │   recorder.py     │      │    app.py        │        │
│  └──────────────────┘      └──────────────────┘        │
└───────────┬─────────────────────────┬───────────────────┘
            │                         │
            ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Business Logic                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │Event Detector│  │Image Manager │  │PPTX Generator  │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
│  ┌─────────────┐  ┌──────────────┐                     │
│  │ Screenshot  │  │   Config     │                     │
│  └─────────────┘  └──────────────┘                     │
└───────────┬─────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PNG Images   │  │ metadata.json │  │   .pptx     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         data/sessions/{session_id}/                     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 レイヤー構成

#### Presentation Layer（プレゼンテーション層）
- **recorder.py**: CLI収録インターフェース
- **app.py**: Streamlit編集UI

#### Business Logic Layer（ビジネスロジック層）
- **utils/event_detector.py**: イベント検知
- **utils/screenshot.py**: スクリーンキャプチャ
- **utils/image_manager.py**: 画像管理・メタデータ
- **exporter/pptx_generator.py**: PowerPoint生成

#### Data Layer（データ層）
- ファイルシステム（JSON + PNG）

---

## 2. モジュール設計

### 2.1 config.py - 設定管理

**責務**: アプリケーション全体の設定値を一元管理

```python
# 主要な設定項目
BASE_DIR: Path                    # プロジェクトルート
DATA_DIR: Path                    # データ保存先
SESSIONS_DIR: Path                # セッション保存先
SCREENSHOT_FORMAT: str            # 画像フォーマット
SCREENSHOT_QUALITY: int           # 画像品質
DETECT_MOUSE_CLICK: bool          # マウス検知ON/OFF
DETECT_KEY_PRESS: bool            # キーボード検知ON/OFF
DEBOUNCE_TIME: float              # デバウンス時間
PPTX_SLIDE_WIDTH: float           # スライド幅
PPTX_SLIDE_HEIGHT: float          # スライド高さ
PPTX_IMAGE_WIDTH_RATIO: float     # 画像配置比率
```

---

### 2.2 utils/screenshot.py - スクリーンショット撮影

**責務**: 画面全体のキャプチャと保存

#### クラス: `ScreenshotCapture`

```python
class ScreenshotCapture:
    """スクリーンショット撮影クラス"""

    def __init__(self, session_dir: Path)
        """初期化
        Args:
            session_dir: 保存先ディレクトリ
        """

    def capture(self) -> Path:
        """画面全体を撮影して保存
        Returns:
            保存したファイルパス
        """

    def close(self):
        """リソース解放"""
```

**使用ライブラリ**: `mss`, `Pillow`

**内部処理フロー**:
1. mss.mss()で画面キャプチャ
2. PIL Imageに変換
3. 連番ファイル名生成（`{counter:04d}_{timestamp}.png`）
4. 指定品質で保存

---

### 2.3 utils/event_detector.py - イベント検知

**責務**: マウス・キーボードイベントの検知とデバウンス処理

#### クラス: `EventDetector`

```python
class EventDetector:
    """イベント検知クラス"""

    def __init__(self, on_event: Callable):
        """初期化
        Args:
            on_event: イベント発生時のコールバック
        """

    def start(self):
        """イベント検知開始"""

    def stop(self):
        """イベント検知停止"""

    def join(self):
        """リスナー終了待機"""

    def _should_trigger(self) -> bool:
        """デバウンス判定"""

    def _on_click(self, x, y, button, pressed):
        """マウスクリックハンドラ"""

    def _on_key_press(self, key):
        """キー押下ハンドラ"""
```

**使用ライブラリ**: `pynput`

**デバウンス処理**:
- 前回イベントから`DEBOUNCE_TIME`秒以上経過した場合のみ発火
- 連続クリック・連打を防ぐ

---

### 2.4 utils/image_manager.py - 画像管理

**責務**: 画像メタデータの管理、編集操作、Undo機能

#### データクラス: `ImageData`

```python
@dataclass
class ImageData:
    """画像データ"""
    filepath: str        # 画像ファイルパス
    description: str     # 説明文
    order: int           # 表示順序
    timestamp: str       # 作成日時（ISO形式）
```

#### クラス: `ImageManager`

```python
class ImageManager:
    """画像管理クラス"""

    def __init__(self, session_dir: Path):
        """初期化
        Args:
            session_dir: セッションディレクトリ
        """

    def add_image(self, filepath: Path) -> ImageData:
        """画像追加"""

    def update_description(self, index: int, description: str):
        """説明文更新"""

    def delete_image(self, index: int):
        """画像削除"""

    def reorder_images(self, new_order: List[int]):
        """順序変更"""

    def undo(self) -> bool:
        """操作取り消し"""

    def get_images(self) -> List[ImageData]:
        """画像リスト取得"""

    def save_metadata(self):
        """メタデータ保存"""

    def _load_metadata(self):
        """メタデータ読み込み"""

    def _auto_detect_images(self):
        """既存画像の自動検出"""

    def _save_state(self):
        """Undo用状態保存"""
```

**データ永続化**:
- `metadata.json`にImageDataのリストをJSON保存
- Undoスタックは最大50件保持
- 全操作で自動保存

---

### 2.5 exporter/pptx_generator.py - PowerPoint生成

**責務**: ImageDataリストからPowerPointファイルを生成

#### クラス: `PPTXGenerator`

```python
class PPTXGenerator:
    """PowerPoint生成クラス"""

    def __init__(self):
        """初期化"""

    def generate(
        self,
        images: List[ImageData],
        output_path: Path,
        title: str = "操作マニュアル"
    ) -> Path:
        """PowerPoint生成
        Args:
            images: 画像データリスト
            output_path: 出力ファイルパス
            title: タイトルスライドのタイトル
        Returns:
            生成したファイルパス
        """

    def _create_title_slide(self, prs, title: str):
        """タイトルスライド作成"""

    def _create_content_slide(
        self,
        prs,
        image_data: ImageData,
        slide_number: int
    ):
        """コンテンツスライド作成"""

    def _add_image_to_slide(self, slide, image_path: Path):
        """スライドに画像を配置"""

    def _add_description_to_slide(self, slide, description: str):
        """スライドに説明文を配置"""
```

**使用ライブラリ**: `python-pptx`

**スライドレイアウト**:
```
┌─────────────────────────────────────┐
│  Step N: {description}              │  ← 上部: 説明文
├─────────────────────────────────────┤
│                                     │
│                                     │
│        [スクリーンショット]          │  ← 中央: 画像（横幅80%）
│                                     │
│                                     │
└─────────────────────────────────────┘
```

---

### 2.6 recorder.py - 収録CLI

**責務**: 収録モードの制御とコンポーネント統合

#### クラス: `Recorder`

```python
class Recorder:
    """収録制御クラス"""

    def __init__(self):
        """初期化（セッションディレクトリ作成）"""

    def start(self):
        """収録開始"""

    def stop(self):
        """収録停止"""

    def _on_event(self):
        """イベントハンドラ（スクリーンショット撮影）"""
```

**処理フロー**:
1. セッションディレクトリ作成（`session_{timestamp}`）
2. ScreenshotCapture初期化
3. ImageManager初期化
4. EventDetector初期化（コールバック: `_on_event`）
5. イベント検知開始
6. Ctrl+C待機
7. 終了処理

---

### 2.7 app.py - Streamlit編集UI

**責務**: 画像編集UIの提供

#### 主要機能

```python
def main():
    """Streamlitメインアプリ"""

def select_session() -> Path:
    """セッション選択UI"""

def display_image_grid(manager: ImageManager):
    """画像一覧グリッド表示"""

def edit_image_description(manager: ImageManager, index: int):
    """説明文編集UI"""

def delete_image_ui(manager: ImageManager, index: int):
    """削除ボタン"""

def undo_button(manager: ImageManager):
    """Undoボタン"""

def reorder_images_ui(manager: ImageManager):
    """並び替えUI"""

def export_pptx_ui(manager: ImageManager):
    """PowerPoint出力UI"""
```

**使用ライブラリ**: `streamlit`

**画面構成**:
```
┌────────────────────────────────────────────┐
│  Manual Maker - 編集モード                 │
├────────────────────────────────────────────┤
│  セッション選択: [dropdown]   [新規作成]    │
├────────────────────────────────────────────┤
│  ┌───┐ ┌───┐ ┌───┐                        │
│  │img│ │img│ │img│  ...                   │
│  │ 1 │ │ 2 │ │ 3 │                        │
│  └───┘ └───┘ └───┘                        │
│  [説明文入力]                               │
│  [削除] [↑] [↓]                            │
├────────────────────────────────────────────┤
│  [Undo] [PowerPoint生成]                   │
└────────────────────────────────────────────┘
```

---

## 3. データフロー

### 3.1 収録フロー

```
User Action (click/key)
    ↓
EventDetector._on_click/key_press()
    ↓
debounce check
    ↓
Recorder._on_event()
    ↓
ScreenshotCapture.capture()
    ↓
ImageManager.add_image()
    ↓
metadata.json保存
```

### 3.2 編集フロー

```
User opens app.py
    ↓
select_session() → session選択
    ↓
ImageManager(session_dir) → metadata読み込み
    ↓
display_image_grid() → 画像表示
    ↓
User edits
    ├→ update_description() → metadata.json更新
    ├→ delete_image() → _save_state() → metadata.json更新
    ├→ reorder_images() → _save_state() → metadata.json更新
    └→ undo() → 前回状態復元 → metadata.json更新
```

### 3.3 出力フロー

```
User clicks "PowerPoint生成"
    ↓
PPTXGenerator.generate()
    ↓
for each ImageData:
    ├→ _create_content_slide()
    ├→ _add_image_to_slide()
    └→ _add_description_to_slide()
    ↓
prs.save(output_path)
    ↓
streamlit download button
```

---

## 4. 状態管理

### 4.1 セッション状態
- セッションディレクトリ: `data/sessions/{session_id}/`
- metadata.json: ImageDataの配列
- PNG画像: 連番ファイル

### 4.2 Undo状態
- ImageManagerがundo_stack保持（最大50件）
- 各編集操作前に`_save_state()`でスナップショット保存
- `undo()`で最新状態をpopして復元

### 4.3 Streamlit状態
- `st.session_state`で現在選択中のセッションを保持
- `st.experimental_rerun()`で画面更新

---

## 5. エラーハンドリング

### 5.1 エラー種別

#### 収録時エラー
- **画面キャプチャ失敗**: mssエラー → ログ出力、スキップ
- **ファイル保存失敗**: IOError → ログ出力、リトライ
- **権限エラー**: PermissionError → ユーザーに通知、停止

#### 編集時エラー
- **metadata破損**: JSONDecodeError → 自動修復試行
- **画像ファイル欠損**: FileNotFoundError → プレースホルダ表示
- **Undoスタック空**: 何もしない

#### 出力時エラー
- **PowerPoint生成失敗**: Exception → エラーメッセージ表示
- **ファイル書き込み失敗**: IOError → 別パス提案

### 5.2 エラー処理方針
- **ログ記録**: すべてのエラーを`logger`に記録
- **ユーザー通知**: 致命的エラーはUIに表示
- **リカバリ**: 可能な限り自動修復
- **データ保護**: エラー時もメタデータは保持

---

## 6. テスト戦略

### 6.1 ユニットテスト対象
- `ScreenshotCapture.capture()`
- `ImageManager`の全メソッド
- `PPTXGenerator.generate()`
- `EventDetector._should_trigger()`

### 6.2 統合テスト
- 収録→編集→出力の一連フロー
- Undo/Redo複数回実行
- セッション切り替え

### 6.3 E2Eテスト（手動）
- 実際のPC操作収録
- 編集UIの操作性
- 生成したPowerPointの確認

---

## 7. パフォーマンス最適化

### 7.1 スクリーンショット
- `mss`ライブラリ使用（高速）
- PNG圧縮品質: 95（バランス）

### 7.2 画像表示
- Streamlitのサムネイル機能活用
- 遅延ロード（将来対応）

### 7.3 メタデータ
- JSON読み書きは必要時のみ
- Undoスタック上限50件

---

## 8. セキュリティ考慮事項

### 8.1 データ保護
- ローカル保存のみ（外部送信なし）
- ファイル権限: ユーザーのみ読み書き

### 8.2 センシティブ情報
- README/起動時に注意喚起
- パスワード入力画面の自動検知（Phase 2）

---

## 9. 拡張性設計

### 9.1 プラグイン構造（将来）
- Exporter抽象クラス
  - PPTXExporter
  - PDFExporter
  - HTMLExporter

### 9.2 設定のカスタマイズ
- `config.py`をYAML化（Phase 2）
- UIから設定変更可能に

---

## 10. デプロイメント

### 10.1 ビルドスクリプト (`build/build.py`)

```python
def build_windows():
    """Windows向けビルド"""

def build_macos():
    """macOS向けビルド"""

def build_all():
    """全プラットフォームビルド"""
```

### 10.2 PyInstaller設定
- `--onefile`: 単一実行ファイル
- `--windowed`: コンソール非表示（UI版のみ）
- `--add-data`: Streamlitリソース同梱
- `--icon`: アプリアイコン

### 10.3 配布パッケージ
```
manual-maker-v1.0.0-windows/
├── ManualMaker.exe
└── README.txt

manual-maker-v1.0.0-macos/
├── ManualMaker.app
└── README.txt
```
