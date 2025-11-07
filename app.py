"""
Streamlit編集UI
収録したスクリーンショットを編集してPowerPointを生成
"""
import streamlit as st
from pathlib import Path
from config import SESSIONS_DIR
from utils.image_manager import ImageManager


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

    # ImageManagerを初期化（セッションステートで管理）
    if "image_manager" not in st.session_state:
        st.session_state.image_manager = ImageManager(session_dir)

    manager = st.session_state.image_manager

    # 画像リストを表示
    images = manager.get_images()

    st.subheader(f"📷 画像一覧 ({len(images)}枚)")

    if len(images) == 0:
        st.warning("このセッションには画像がありません")
        return

    # 画像グリッド表示（3列）
    display_image_grid(images)


def display_image_grid(images):
    """
    画像を3列グリッドで表示

    Args:
        images: ImageDataのリスト
    """
    # 3列グリッド
    cols_per_row = 3

    for i in range(0, len(images), cols_per_row):
        cols = st.columns(cols_per_row)

        for col_idx, col in enumerate(cols):
            img_idx = i + col_idx

            if img_idx >= len(images):
                break

            img_data = images[img_idx]
            img_path = Path(img_data.filepath)

            with col:
                if img_path.exists():
                    # サムネイル表示
                    st.image(
                        str(img_path),
                        use_container_width=True,
                        caption=f"#{img_idx + 1}"
                    )

                    # 説明文表示
                    if img_data.description:
                        st.caption(f"📝 {img_data.description}")
                    else:
                        st.caption("📝 （説明なし）")

                    # ファイル名表示
                    st.caption(f"📄 `{img_path.name}`")
                else:
                    st.error(f"画像が見つかりません: {img_path.name}")


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
