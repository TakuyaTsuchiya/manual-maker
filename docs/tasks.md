# Manual Maker - 実装タスクリスト

## Phase 1: MVP実装（TDD）

---

## ✅ 完了済み

### Task 0: プロジェクト初期化
- [x] プロジェクト構造作成
- [x] requirements.txt作成
- [x] .gitignore設定
- [x] README.md作成
- [x] GitHubリポジトリ作成

### Task 1: 収録機能（Recorder）
- [x] config.py実装
- [x] utils/screenshot.py実装
- [x] utils/event_detector.py実装
- [x] utils/image_manager.py実装
- [x] recorder.py実装（CLI）

---

## 🚧 Phase 1: TDD開発

### Task 2: テスト環境構築
**優先度**: 🔴 高
**依存**: なし
**担当モジュール**: テスト基盤

#### サブタスク
- [ ] 2.1 `pytest`とテスト関連ライブラリをrequirements.txtに追加
  - pytest
  - pytest-cov (カバレッジ)
  - pytest-mock (モック)
- [ ] 2.2 `tests/`ディレクトリ構造作成
  ```
  tests/
  ├── __init__.py
  ├── conftest.py          # pytest共通設定
  ├── fixtures/            # テストデータ
  ├── test_screenshot.py
  ├── test_event_detector.py
  ├── test_image_manager.py
  └── test_pptx_generator.py
  ```
- [ ] 2.3 `pytest.ini`作成（テスト設定）
- [ ] 2.4 `conftest.py`に共通フィクスチャ作成
  - `temp_session_dir`: 一時セッションディレクトリ
  - `sample_images`: テスト用画像データ
  - `mock_screenshot`: モックスクリーンショット

#### 完了条件 (DoD)
- [ ] `pytest`コマンドでテストが実行できる
- [ ] カバレッジレポートが生成できる
- [ ] 共通フィクスチャが他のテストで利用可能

---

### Task 2.5: クラッシュ対策の実装（オプション - Phase 2に延期可能）
**優先度**: 🟡 中
**依存**: Task 2
**担当モジュール**: 全モジュール
**備考**: docs/crash-prevention.mdに設計済み。Phase 1では既存のリアルタイム保存で対応し、Phase 2以降で完全実装を検討。

#### サブタスク（Phase 2以降で実装）
- [ ] 2.5.1 .lockファイルによるクラッシュリカバリ機能
- [ ] 2.5.2 堅牢なエラーハンドリング追加
- [ ] 2.5.3 リソース管理の改善（context manager）
- [ ] 2.5.4 ロギング機能の追加
- [ ] 2.5.5 定期チェックポイント機能

#### 完了条件 (DoD)
- [ ] クラッシュ時もデータが保護される
- [ ] 復旧UIが機能する
- [ ] テストで安定性を検証

---

### Task 3: ImageManagerのテスト作成（既存コード）
**優先度**: 🔴 高
**依存**: Task 2
**担当モジュール**: `utils/image_manager.py`

#### サブタスク
- [ ] 3.1 `test_image_manager.py`作成
- [ ] 3.2 テスト: `add_image()` - 画像追加
- [ ] 3.3 テスト: `update_description()` - 説明文更新
- [ ] 3.4 テスト: `delete_image()` - 画像削除
- [ ] 3.5 テスト: `reorder_images()` - 順序変更
- [ ] 3.6 テスト: `undo()` - Undo機能
- [ ] 3.7 テスト: `save_metadata()`/`_load_metadata()` - 永続化
- [ ] 3.8 テスト: `_auto_detect_images()` - 既存画像検出
- [ ] 3.9 エッジケース: 空リスト、存在しないインデックス
- [ ] 3.10 既存実装のバグ修正（見つかった場合）

#### 完了条件 (DoD)
- [ ] すべてのパブリックメソッドにテストがある
- [ ] カバレッジ90%以上
- [ ] すべてのテストがパス

---

### Task 4: PowerPoint生成機能（TDD）
**優先度**: 🔴 高
**依存**: Task 2
**担当モジュール**: `exporter/pptx_generator.py`

#### サブタスク

##### 4.1 Red: テスト作成
- [ ] 4.1.1 `test_pptx_generator.py`作成
- [ ] 4.1.2 テスト: 空のプレゼンテーション生成
- [ ] 4.1.3 テスト: タイトルスライド作成
- [ ] 4.1.4 テスト: 1枚の画像スライド生成
- [ ] 4.1.5 テスト: 複数画像スライド生成
- [ ] 4.1.6 テスト: 説明文の配置
- [ ] 4.1.7 テスト: 画像のサイズ調整
- [ ] 4.1.8 テスト: 出力ファイルの存在確認
- [ ] 4.1.9 テスト: 生成されたPPTXがOfficeで開けるか（手動）

##### 4.2 Green: 実装
- [ ] 4.2.1 `exporter/__init__.py`作成
- [ ] 4.2.2 `PPTXGenerator`クラス作成
- [ ] 4.2.3 `generate()`メソッド実装
- [ ] 4.2.4 `_create_title_slide()`実装
- [ ] 4.2.5 `_create_content_slide()`実装
- [ ] 4.2.6 `_add_image_to_slide()`実装
- [ ] 4.2.7 `_add_description_to_slide()`実装
- [ ] 4.2.8 画像アスペクト比の保持実装
- [ ] 4.2.9 すべてのテストをパスさせる

##### 4.3 Refactor: リファクタリング
- [ ] 4.3.1 レイアウト定数の外部化
- [ ] 4.3.2 エラーハンドリング追加
- [ ] 4.3.3 docstring追加

#### 完了条件 (DoD)
- [ ] すべてのテストがパス
- [ ] カバレッジ85%以上
- [ ] 実際のPowerPointファイルが正しく生成される
- [ ] Office/LibreOfficeで開ける

---

### Task 5: Streamlit編集UI実装
**優先度**: 🟡 中
**依存**: Task 3, Task 4
**担当モジュール**: `app.py`

#### サブタスク

##### 5.1 基本UI
- [ ] 5.1.1 `app.py`作成
- [ ] 5.1.2 `main()`関数実装
- [ ] 5.1.3 セッション選択UI実装
- [ ] 5.1.4 ImageManager初期化

##### 5.2 画像表示UI
- [ ] 5.2.1 `display_image_grid()`実装
- [ ] 5.2.2 サムネイル表示（3列グリッド）
- [ ] 5.2.3 画像クリックで拡大表示

##### 5.3 編集UI
- [ ] 5.3.1 `edit_image_description()`実装
- [ ] 5.3.2 説明文入力フォーム
- [ ] 5.3.3 削除ボタン実装
- [ ] 5.3.4 Undoボタン実装
- [ ] 5.3.5 並び替えUI実装（上下ボタン）

##### 5.4 出力UI
- [ ] 5.4.1 `export_pptx_ui()`実装
- [ ] 5.4.2 PowerPoint生成ボタン
- [ ] 5.4.3 ダウンロードボタン
- [ ] 5.4.4 プログレスバー表示

##### 5.5 UX改善
- [ ] 5.5.1 操作完了時のトースト通知
- [ ] 5.5.2 確認ダイアログ（削除時）
- [ ] 5.5.3 エラーメッセージ表示
- [ ] 5.5.4 空セッション時のガイド表示

#### 完了条件 (DoD)
- [ ] `streamlit run app.py`で起動する
- [ ] すべての編集機能が動作する
- [ ] PowerPointが生成できる
- [ ] UIが直感的で使いやすい

---

### Task 6: 統合テスト
**優先度**: 🟡 中
**依存**: Task 3, Task 4, Task 5
**担当モジュール**: 全体

#### サブタスク
- [ ] 6.1 `tests/test_integration.py`作成
- [ ] 6.2 テスト: 収録→編集→出力の完全フロー
- [ ] 6.3 テスト: セッションの読み込み・保存
- [ ] 6.4 テスト: 複数回のUndo/Redo
- [ ] 6.5 テスト: 大量画像（100枚）の処理
- [ ] 6.6 手動E2Eテスト実施
  - 実際のPC操作を収録
  - 編集UIで編集
  - PowerPoint生成・確認

#### 完了条件 (DoD)
- [ ] 統合テストがすべてパス
- [ ] 手動E2Eテストで問題なし
- [ ] パフォーマンス要件を満たす

---

### Task 7: ビルド機能（PyInstaller）
**優先度**: 🟢 低
**依存**: Task 6
**担当モジュール**: `build/build.py`

#### サブタスク

##### 7.1 ビルドスクリプト作成
- [ ] 7.1.1 `build/build.py`作成
- [ ] 7.1.2 `build_windows()`関数実装
- [ ] 7.1.3 `build_macos()`関数実装
- [ ] 7.1.4 PyInstaller設定（.specファイル）
- [ ] 7.1.5 アイコン画像作成・配置

##### 7.2 Windows版ビルド
- [ ] 7.2.1 Windows環境でビルド実行
- [ ] 7.2.2 exeファイル動作確認
- [ ] 7.2.3 recorder.exe動作確認
- [ ] 7.2.4 app.exe動作確認
- [ ] 7.2.5 配布パッケージ作成

##### 7.3 macOS版ビルド
- [ ] 7.3.1 macOS環境でビルド実行
- [ ] 7.3.2 .appファイル動作確認
- [ ] 7.3.3 画面収録権限の許可フロー確認
- [ ] 7.3.4 配布パッケージ作成

##### 7.4 ドキュメント
- [ ] 7.4.1 ビルド手順をREADMEに追記
- [ ] 7.4.2 配布パッケージのREADME作成
- [ ] 7.4.3 インストールガイド作成

#### 完了条件 (DoD)
- [ ] Windows版がビルドできる
- [ ] macOS版がビルドできる
- [ ] ビルド済みアプリが正常動作する
- [ ] 配布パッケージが完成

---

### Task 8: ドキュメント整備
**優先度**: 🟢 低
**依存**: Task 7
**担当モジュール**: ドキュメント

#### サブタスク
- [ ] 8.1 README.md更新
  - 機能一覧
  - スクリーンショット追加
  - インストール手順
  - 使い方（動画/GIF）
- [ ] 8.2 CHANGELOG.md作成
- [ ] 8.3 LICENSE追加（MIT）
- [ ] 8.4 CONTRIBUTING.md作成
- [ ] 8.5 コードコメント・docstring見直し

#### 完了条件 (DoD)
- [ ] README.mdが完全で分かりやすい
- [ ] すべてのpublicメソッドにdocstringがある
- [ ] ライセンスが明記されている

---

### Task 9: Phase 1 完成・リリース
**優先度**: 🔴 高
**依存**: Task 1-8
**担当モジュール**: 全体

#### サブタスク
- [ ] 9.1 全機能の動作確認
- [ ] 9.2 バグ修正
- [ ] 9.3 コードレビュー
- [ ] 9.4 パフォーマンスチェック
- [ ] 9.5 GitHubにv1.0.0タグ作成
- [ ] 9.6 Releaseページ作成
- [ ] 9.7 配布パッケージアップロード
- [ ] 9.8 リリースノート作成

#### 完了条件 (DoD)
- [ ] すべてのテストがパス
- [ ] カバレッジ80%以上
- [ ] 既知の致命的バグがない
- [ ] Windows/macOS両対応
- [ ] GitHubにリリース済み

---

## 📊 進捗管理

### タスク優先度
- 🔴 高: 必須機能、ブロッカー
- 🟡 中: 重要だが後回し可能
- 🟢 低: 補助的機能

### 現在のステータス
- ✅ 完了: Task 0, Task 1
- 🚧 進行中: Task 2（次）
- ⏳ 未着手: Task 3-9

### TDDサイクル
各タスクで以下を繰り返す：
1. **Red**: テストを書く（失敗）
2. **Green**: 最小限の実装でテストをパス
3. **Refactor**: コードを整理

---

## 🎯 Phase 2以降のロードマップ（参考）

### Phase 2: 画像注釈機能（4週間）
- [ ] 画像編集UI実装（矢印・枠線・テキスト）
- [ ] 注釈データの永続化
- [ ] PowerPoint出力への注釈反映

### Phase 3: 高度な機能（6週間）
- [ ] テンプレート機能
- [ ] 特定ウィンドウのみ収録
- [ ] PDF/HTML出力
- [ ] ホットキーカスタマイズ

### Phase 4: クラウド対応（8週間）
- [ ] クラウドストレージ連携
- [ ] チーム共有機能
- [ ] バージョン管理

---

## 📝 次のアクション

### 今すぐ実施
1. Task 2: テスト環境構築
2. Task 3: ImageManagerのテスト作成

### 今週中に完了
- Task 2-4: テスト環境 + PowerPoint生成（TDD）

### 2週間以内に完了
- Task 5-7: Streamlit UI + ビルド

---

## 🐛 既知の問題・TODO

### 既存コードの改善点
- [ ] recorder.pyのシグナルハンドラの二重定義
- [ ] config.pyのディレクトリ自動作成タイミング
- [ ] ImageManagerのUndoスタック上限処理の最適化

### 将来の技術的負債
- [ ] metadata.jsonをSQLiteに移行（大量画像対応）
- [ ] 非同期処理の導入（パフォーマンス改善）
- [ ] ロギング機能の強化

---

## 📚 参考資料

### ドキュメント
- [要件定義書](./requirements.md)
- [設計書](./design.md)

### 技術ドキュメント
- [pytest公式](https://docs.pytest.org/)
- [python-pptx公式](https://python-pptx.readthedocs.io/)
- [Streamlit公式](https://docs.streamlit.io/)
- [PyInstaller公式](https://pyinstaller.org/)

### TDD参考
- Test-Driven Development by Example (Kent Beck)
- [TDDベストプラクティス](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
