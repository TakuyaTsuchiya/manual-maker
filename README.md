# Manual Maker - マニュアル自動作成アプリ

PC画面操作を自動記録し、PowerPointマニュアルを生成するデスクトップアプリケーション

## 機能

- **収録モード**: マウスクリック/キー入力を検知し、自動でスクリーンショットを撮影
- **編集モード**: スクリーンショット一覧の表示・編集、説明文の追加、並び替え
- **PowerPoint出力**: 1スライド = 1画像 + 説明文の形式でマニュアルを自動生成

## インストール

```bash
# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使い方

### 1. 収録開始

```bash
python recorder.py
```

マウスクリックやキー入力を検知すると自動でスクリーンショットが保存されます。
Ctrl+Cで収録を停止します。

### 2. 編集

```bash
streamlit run app.py
```

ブラウザで編集画面が開きます。各画像に説明文を追加し、不要な画像を削除できます。

### 3. PowerPoint出力

編集画面から「PowerPoint生成」ボタンをクリックすると、マニュアルが作成されます。

## プロジェクト構成

```
manual-maker/
├── recorder.py              # 画面監視・スクリーンショット撮影
├── app.py                   # Streamlit編集UI
├── config.py                # 設定管理
├── utils/
│   ├── screenshot.py        # スクリーンショット処理
│   ├── event_detector.py    # マウス/キーボード検知
│   └── image_manager.py     # 画像管理・Undo
└── exporter/
    └── pptx_generator.py    # PowerPoint生成
```

## ビルド（exe化）

```bash
python build/build.py
```

`dist/`フォルダに実行ファイルが生成されます。

## ライセンス

MIT License
