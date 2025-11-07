# Manual Maker - ビルドガイド

PyInstallerを使用してWindows/macOS用の実行ファイルを作成する手順です。

## 前提条件

- Python 3.9以上
- PyInstaller (`pip install pyinstaller`)
- すべての依存パッケージがインストール済み (`pip install -r requirements.txt`)

## ビルド方法

### 1. 自動ビルド（プラットフォーム自動検出）

```bash
cd manual-maker
python build/build.py
```

現在のプラットフォームを自動検出してビルドします。

### 2. 手動ビルド（プラットフォーム指定）

**Windows版をビルド:**
```bash
python build/build.py windows
```

**macOS版をビルド:**
```bash
python build/build.py macos
```

## 出力ファイル

ビルド成功後、以下のディレクトリに実行ファイルが生成されます:

### Windows版
```
dist/windows/
├── recorder.exe        # スクリーンショット収録ツール
└── manual-maker-app.exe  # 編集UIアプリ
```

### macOS版
```
dist/macos/
├── recorder.app         # スクリーンショット収録ツール
└── manual-maker-app.app   # 編集UIアプリ
```

## 使い方

### Recorder（収録ツール）

1. `recorder.exe` (Windows) または `recorder.app` (macOS) を実行
2. `Ctrl+Shift+S` で収録開始
3. PC操作を実行（自動的にスクリーンショット撮影）
4. `Ctrl+Shift+Q` で収録終了

### Manual Maker App（編集UI）

1. `manual-maker-app.exe` (Windows) または `manual-maker-app.app` (macOS) を実行
2. ブラウザが開き、Streamlit UIが表示されます
3. セッションを選択して編集
4. PowerPointファイルを生成・ダウンロード

## トラブルシューティング

### PyInstallerがインストールされていない

```bash
pip install pyinstaller
```

### 実行ファイルが起動しない

- アンチウイルスソフトが実行をブロックしている可能性があります
- Windows: 「詳細情報」→「実行」で許可
- macOS: システム環境設定 → セキュリティとプライバシー → 「このまま開く」

### macOSで画面収録権限エラー

1. システム環境設定 → セキュリティとプライバシー
2. 「プライバシー」タブ → 「画面収録」
3. `recorder.app` にチェックを入れる
4. アプリを再起動

## 配布パッケージの作成

ビルド後、以下のファイルをZIPにまとめて配布:

```
manual-maker-v1.0-windows.zip
├── recorder.exe
├── manual-maker-app.exe
└── README.txt (使い方説明)

manual-maker-v1.0-macos.zip
├── recorder.app
├── manual-maker-app.app
└── README.txt (使い方説明)
```

## 開発者向けメモ

### ビルド設定のカスタマイズ

`build/build.py`を編集して以下をカスタマイズ可能:

- アイコン (`--icon=icon.ico`)
- 追加データファイル (`--add-data`)
- 隠しインポート (`--hidden-import`)
- ワンファイル化 (`--onefile`) / ワンディレクトリ化 (`--onedir`)

### クリーンビルド

```bash
# ビルドキャッシュをクリア
rm -rf build/ dist/ *.spec
python build/build.py
```

## 参考資料

- [PyInstaller公式ドキュメント](https://pyinstaller.org/)
- [Streamlitのデプロイガイド](https://docs.streamlit.io/)
