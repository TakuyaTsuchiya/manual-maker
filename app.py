"""
Streamlit編集UI
収録したスクリーンショットを編集してPowerPointを生成
"""
import streamlit as st
from pathlib import Path
from config import SESSIONS_DIR


def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="Manual Maker - 編集UI",
        page_icon="📸",
        layout="wide"
    )

    st.title("📸 Manual Maker - 編集UI")
    st.markdown("収録したスクリーンショットを編集してPowerPointマニュアルを生成します")

    # セッション選択
    session_dir = select_session()

    if session_dir is None:
        st.info("👈 左サイドバーからセッションを選択してください")
        st.markdown("""
        ### 使い方
        1. 左サイドバーから編集したいセッションを選択
        2. 画像を確認して説明文を追加
        3. 必要に応じて画像を削除・並び替え
        4. PowerPointファイルを生成してダウンロード
        """)
        return

    st.success(f"セッション: `{session_dir.name}`")


def select_session() -> Path | None:
    """
    セッション選択UI

    Returns:
        Path | None: 選択されたセッションディレクトリ、未選択の場合はNone
    """
    st.sidebar.header("セッション選択")

    # sessions/ ディレクトリ内のセッション一覧を取得
    if not SESSIONS_DIR.exists():
        st.sidebar.error(f"セッションディレクトリが見つかりません: {SESSIONS_DIR}")
        return None

    session_dirs = sorted(
        [d for d in SESSIONS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True  # 新しい順
    )

    if not session_dirs:
        st.sidebar.warning("セッションがありません")
        st.sidebar.info("まず `python recorder.py` でスクリーンショットを収録してください")
        return None

    # セッション名のリスト（フォルダ名）
    session_names = [d.name for d in session_dirs]

    # セレクトボックスで選択
    selected_name = st.sidebar.selectbox(
        "編集するセッションを選択",
        options=session_names,
        help="最新のセッションが上に表示されます"
    )

    if selected_name:
        selected_dir = SESSIONS_DIR / selected_name
        return selected_dir

    return None


if __name__ == "__main__":
    main()
