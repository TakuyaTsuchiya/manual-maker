# Manual Maker - クラッシュ防止・データ損失対策設計書

## 1. 問題の背景

### 1.1 参考アプリ（Process Recorder）の課題
- 頻繁にクラッシュする
- クラッシュ時に記録したデータが保存されずに消える
- ユーザー体験の大幅な低下

### 1.2 クラッシュの主な原因（推測）
1. **メモリリーク**: 長時間収録で画像をメモリに蓄積
2. **ファイルI/O失敗**: 保存処理中のクラッシュ
3. **イベント処理の過負荷**: 高頻度操作で処理が追いつかない
4. **リソース枯渇**: スクリーンキャプチャリソースの未解放
5. **OS権限問題**: 画面録画権限の喪失
6. **同期処理のブロック**: 重い処理でUIがフリーズ

---

## 2. 設計方針

### 2.1 基本原則
1. **Fail-Safe**: クラッシュしても最小限のデータ損失に留める
2. **即座の永続化**: すべてのデータを即座にディスクに保存
3. **堅牢なエラーハンドリング**: 一部のエラーで全体が落ちない
4. **リソース管理**: メモリ・ファイルハンドル等の適切な解放
5. **復旧可能性**: クラッシュ後の自動復旧機能

---

## 3. 対策の実装

### 3.1 リアルタイム保存（既に実装済み）

#### 現在の設計
```python
# recorder.py の _on_event()
def _on_event(self):
    # スクリーンショット撮影 → 即座にPNGファイル保存
    filepath = self.screenshot.capture()

    # メタデータ更新 → 即座にJSONファイル保存
    self.image_manager.add_image(filepath)
```

#### メリット
- ✅ 各操作で即座にディスク書き込み
- ✅ クラッシュしても既存の画像は残る
- ✅ メモリに大量データを保持しない

#### 改善点
- メタデータの原子性を確保（一時ファイル経由で保存）

---

### 3.2 クラッシュリカバリ機能

#### 設計
収録セッション開始時に`.lock`ファイルを作成し、正常終了時に削除。
次回起動時に`.lock`が残っていれば異常終了と判断し、復旧を提案。

#### 実装

##### recorder.py の改善
```python
class Recorder:
    def __init__(self):
        # ... 既存のコード ...
        self.lock_file = self.session_dir / ".lock"
        self._create_lock()

    def _create_lock(self):
        """ロックファイル作成"""
        self.lock_file.write_text(json.dumps({
            "started_at": datetime.now().isoformat(),
            "pid": os.getpid()
        }))

    def stop(self):
        """収録停止"""
        self.event_detector.stop()
        self.screenshot.close()
        self._remove_lock()  # 正常終了時に削除
        # ... 既存のコード ...

    def _remove_lock(self):
        """ロックファイル削除"""
        if self.lock_file.exists():
            self.lock_file.unlink()
```

##### app.py での復旧UI
```python
def check_crashed_sessions() -> List[Path]:
    """クラッシュしたセッションを検出"""
    crashed = []
    for session_dir in config.SESSIONS_DIR.iterdir():
        lock_file = session_dir / ".lock"
        if lock_file.exists():
            crashed.append(session_dir)
    return crashed

def recovery_ui():
    """復旧UI"""
    crashed = check_crashed_sessions()
    if crashed:
        st.warning("前回のセッションが異常終了しました。")
        for session_dir in crashed:
            if st.button(f"復旧: {session_dir.name}"):
                # ロックファイル削除
                (session_dir / ".lock").unlink()
                st.success("復旧しました。このセッションを編集できます。")
```

---

### 3.3 堅牢なエラーハンドリング

#### 設計
各処理を`try-except`で保護し、エラーが発生しても続行可能にする。

#### 実装

##### screenshot.py の改善
```python
def capture(self) -> Optional[Path]:
    """画面キャプチャ（エラーハンドリング強化版）"""
    try:
        # タイムスタンプ付きファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.counter:04d}_{timestamp}.{config.SCREENSHOT_FORMAT}"
        filepath = self.session_dir / filename

        # スクリーンショット撮影
        screenshot = self.sct.grab(self.sct.monitors[0])

        # PIL Imageに変換して保存
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(filepath, quality=config.SCREENSHOT_QUALITY)

        self.counter += 1
        logger.info(f"Screenshot saved: {filepath.name}")
        print(f"📸 Screenshot saved: {filepath.name}")

        return filepath

    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}", exc_info=True)
        print(f"⚠️  Screenshot capture failed: {e}")
        return None  # エラーでもNoneを返して続行
```

##### recorder.py の改善
```python
def _on_event(self):
    """イベントハンドラ（エラーハンドリング強化版）"""
    try:
        filepath = self.screenshot.capture()
        if filepath:  # 成功時のみ追加
            self.image_manager.add_image(filepath)
        else:
            logger.warning("Screenshot capture returned None, skipping")
    except Exception as e:
        logger.error(f"Error in event handler: {e}", exc_info=True)
        print(f"⚠️  Error occurred but continuing: {e}")
        # クラッシュせずに続行
```

##### image_manager.py の改善
```python
def save_metadata(self):
    """メタデータ保存（原子性を確保）"""
    try:
        data = [asdict(img) for img in self.images]

        # 一時ファイルに書き込み
        temp_file = self.metadata_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # アトミックに置き換え
        temp_file.replace(self.metadata_file)

    except Exception as e:
        logger.error(f"Failed to save metadata: {e}", exc_info=True)
        # 失敗しても既存のmetadata.jsonは破損しない
```

---

### 3.4 リソース管理の改善

#### 設計
- mssオブジェクトの適切なクローズ
- context managerの活用
- finally句でのリソース解放保証

#### 実装

##### screenshot.py の改善
```python
class ScreenshotCapture:
    def __enter__(self):
        """Context manager: 開始"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: 終了時に必ずクローズ"""
        self.close()

    def close(self):
        """リソース解放"""
        try:
            if hasattr(self, 'sct') and self.sct:
                self.sct.close()
                logger.info("Screenshot capture resources released")
        except Exception as e:
            logger.error(f"Error closing screenshot capture: {e}")
```

##### recorder.py の改善
```python
def start(self):
    """収録開始"""
    try:
        self.event_detector.start()
        self.event_detector.join()
    except KeyboardInterrupt:
        self.stop()
    except Exception as e:
        logger.error(f"Unexpected error in recorder: {e}", exc_info=True)
        self.stop()
    finally:
        # 必ずリソース解放
        self._cleanup()

def _cleanup(self):
    """リソース解放"""
    try:
        self.screenshot.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
```

---

### 3.5 ロギング機能

#### 設計
Pythonの`logging`モジュールを使用し、以下のログを記録：
- エラー・警告
- 収録開始・停止
- スクリーンショット撮影
- メタデータ保存

#### 実装

##### config.py に追加
```python
import logging
from logging.handlers import RotatingFileHandler

# ログディレクトリ
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ロガー設定
def setup_logger(name: str) -> logging.Logger:
    """ロガーのセットアップ"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # ファイルハンドラ（最大5MB、3世代保持）
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # フォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

##### 各モジュールでの使用
```python
# recorder.py
import config
logger = config.setup_logger('recorder')

# screenshot.py
import config
logger = config.setup_logger('screenshot')

# image_manager.py
import config
logger = config.setup_logger('image_manager')
```

---

### 3.6 定期チェックポイント

#### 設計
N枚ごとにバックアップメタデータを作成

#### 実装

##### image_manager.py に追加
```python
CHECKPOINT_INTERVAL = 10  # 10枚ごと

def add_image(self, filepath: Path) -> ImageData:
    """画像追加（チェックポイント機能付き）"""
    self._save_state()
    img_data = ImageData(filepath=str(filepath), order=len(self.images))
    self.images.append(img_data)
    self.save_metadata()

    # チェックポイント作成
    if len(self.images) % CHECKPOINT_INTERVAL == 0:
        self.create_checkpoint()

    return img_data

def create_checkpoint(self):
    """チェックポイント作成"""
    try:
        checkpoint_file = self.session_dir / f"metadata_checkpoint_{len(self.images)}.json"
        data = [asdict(img) for img in self.images]
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Checkpoint created: {checkpoint_file.name}")
    except Exception as e:
        logger.error(f"Failed to create checkpoint: {e}")
```

---

### 3.7 メモリ監視（将来実装）

#### 設計
`psutil`を使用してメモリ使用量を監視

#### 実装例
```python
import psutil

def check_memory_usage():
    """メモリ使用量チェック"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    if memory_mb > 1000:  # 1GB超過
        logger.warning(f"High memory usage: {memory_mb:.1f}MB")
        return False
    return True
```

---

### 3.8 手動保存ボタン（将来実装）

#### 設計
収録中でも途中で「今すぐ保存」を実行可能

#### 実装案
- ホットキー（例: F5）で即座に保存確認
- 現在のセッション情報を表示

---

## 4. テスト計画

### 4.1 ユニットテスト

#### test_crash_recovery.py
```python
def test_lock_file_creation():
    """ロックファイルが作成されるか"""

def test_lock_file_removal():
    """正常終了時にロックファイルが削除されるか"""

def test_crashed_session_detection():
    """クラッシュセッションを検出できるか"""

def test_metadata_atomic_save():
    """メタデータ保存の原子性"""

def test_error_handling_continues():
    """エラー発生後も処理が続行するか"""
```

#### test_resource_management.py
```python
def test_screenshot_context_manager():
    """context managerでリソース解放されるか"""

def test_cleanup_on_exception():
    """例外発生時もcleanupが実行されるか"""
```

### 4.2 統合テスト

#### test_stability.py
```python
def test_long_session_stability():
    """長時間収録の安定性（100枚以上）"""

def test_high_frequency_events():
    """高頻度イベント時の安定性"""

def test_memory_leak():
    """メモリリークが発生しないか"""
```

### 4.3 手動テスト

- [ ] 収録中に強制終了 → 復旧UIが表示されるか
- [ ] 長時間収録（1000枚以上）で安定動作するか
- [ ] エラー発生時もクラッシュしないか
- [ ] ログファイルが正しく記録されるか

---

## 5. ユーザー向けガイドライン

### 5.1 推奨事項
- 定期的に収録を停止して内容を確認
- 1セッションあたり500枚以下を推奨
- 重要な操作前に一度停止して保存確認

### 5.2 トラブルシューティング
#### クラッシュした場合
1. アプリを再起動
2. 「復旧」ボタンをクリック
3. セッションが復元される

#### 画像が一部欠損している場合
- チェックポイントから復元可能
- logs/recorder.logを確認してエラー原因を特定

---

## 6. 実装優先度

### Phase 1（必須）
- [x] リアルタイム保存の確認・改善
- [ ] クラッシュリカバリ機能（.lock）
- [ ] 堅牢なエラーハンドリング
- [ ] リソース管理の改善
- [ ] ロギング機能

### Phase 2
- [ ] 定期チェックポイント
- [ ] 復旧UIの洗練

### Phase 3（将来）
- [ ] メモリ監視
- [ ] 手動保存ボタン
- [ ] 自動バックアップ

---

## 7. パフォーマンス影響

### 7.1 オーバーヘッド
- ロギング: 微小（数ms）
- 原子性保存: 微小（一時ファイル作成のみ）
- チェックポイント: 10枚ごとに数十ms

### 7.2 最適化
- 非同期ログ書き込み（将来検討）
- バックグラウンド保存（将来検討）

---

## 8. まとめ

### 8.1 主要な対策
1. ✅ **リアルタイム保存**: 既に実装済み
2. 🚧 **クラッシュリカバリ**: .lockファイルで復旧可能に
3. 🚧 **エラーハンドリング**: クラッシュせず続行
4. 🚧 **リソース管理**: 適切な解放を保証
5. 🚧 **ロギング**: 問題の追跡と診断

### 8.2 期待される効果
- **データ損失リスク**: ほぼゼロ
- **安定性**: 大幅向上
- **ユーザー体験**: 安心して長時間収録可能
- **デバッグ性**: ログによる問題特定が容易

これにより、Process Recorderのような「クラッシュして記録が消える」問題を根本的に解決できます。
