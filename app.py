"""
Streamlit編集UI
収録したスクリーンショットを編集してPowerPointを生成
"""
import streamlit as st
from pathlib import Path
from config import SESSIONS_DIR
from utils.image_manager import ImageManager
from exporter.pptx_generator import PPTXGenerator


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

    # Undoボタン（画像リストの上部に配置）
    if len(manager.undo_stack) > 0:
        if st.button(f"↩️ 元に戻す ({len(manager.undo_stack)}件)"):
            if manager.undo():
                st.success("✅ 操作を元に戻しました")
                st.rerun()

    # 画像グリッド表示（3列）
    display_image_grid(images)

    # PowerPoint生成UI
    st.divider()
    export_pptx_ui(session_dir, manager, images)


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

                    # アクションボタン行
                    btn_cols = st.columns([1, 1, 2])

                    with btn_cols[0]:
                        # 上に移動ボタン
                        if img_idx > 0:
                            if st.button("⬆️", key=f"up_{img_idx}"):
                                manager = st.session_state.image_manager
                                # 現在の順序を取得して入れ替え
                                current_order = list(range(len(images)))
                                current_order[img_idx], current_order[img_idx - 1] = \
                                    current_order[img_idx - 1], current_order[img_idx]
                                manager.reorder_images(current_order)
                                st.rerun()

                    with btn_cols[1]:
                        # 下に移動ボタン
                        if img_idx < len(images) - 1:
                            if st.button("⬇️", key=f"down_{img_idx}"):
                                manager = st.session_state.image_manager
                                # 現在の順序を取得して入れ替え
                                current_order = list(range(len(images)))
                                current_order[img_idx], current_order[img_idx + 1] = \
                                    current_order[img_idx + 1], current_order[img_idx]
                                manager.reorder_images(current_order)
                                st.rerun()

                    with btn_cols[2]:
                        # 削除ボタン
                        if st.button("🗑️ 削除", key=f"delete_{img_idx}", type="secondary"):
                            # 確認用のセッションステート
                            st.session_state[f"confirm_delete_{img_idx}"] = True
                            st.rerun()

                    # 削除確認ダイアログ
                    if st.session_state.get(f"confirm_delete_{img_idx}", False):
                        with st.expander("⚠️ 削除の確認", expanded=True):
                            st.warning(f"画像#{img_idx + 1}を削除しますか？この操作は元に戻すことができます（Undoボタン）。")
                            confirm_cols = st.columns(2)
                            with confirm_cols[0]:
                                if st.button("✅ 削除する", key=f"confirm_yes_{img_idx}", type="primary"):
                                    manager = st.session_state.image_manager
                                    manager.delete_image(img_idx)
                                    st.session_state[f"confirm_delete_{img_idx}"] = False
                                    st.success(f"✅ 画像#{img_idx + 1}を削除しました")
                                    st.rerun()
                            with confirm_cols[1]:
                                if st.button("❌ キャンセル", key=f"confirm_no_{img_idx}"):
                                    st.session_state[f"confirm_delete_{img_idx}"] = False
                                    st.rerun()

                    # 説明文編集フォーム
                    with st.expander("✏️ 説明文を編集", expanded=False):
                        edit_description_form(img_idx, img_data)

                    # 現在の説明文表示
                    if img_data.description:
                        st.caption(f"📝 {img_data.description}")
                    else:
                        st.caption("📝 （説明なし）")

                    # ファイル名表示
                    st.caption(f"📄 `{img_path.name}`")
                else:
                    st.error(f"画像が見つかりません: {img_path.name}")


def edit_description_form(img_idx: int, img_data):
    """
    説明文編集フォーム

    Args:
        img_idx: 画像のインデックス
        img_data: ImageDataオブジェクト
    """
    manager = st.session_state.image_manager

    # 現在の説明文を初期値として表示
    current_desc = img_data.description or ""

    new_desc = st.text_area(
        "説明文",
        value=current_desc,
        key=f"desc_input_{img_idx}",
        height=100,
        placeholder="この操作の説明を入力してください..."
    )

    # 保存ボタン
    if st.button("💾 保存", key=f"save_desc_{img_idx}"):
        if new_desc != current_desc:
            manager.update_description(img_idx, new_desc)
            st.success("✅ 説明文を更新しました")
            st.rerun()
        else:
            st.info("変更がありません")


def export_pptx_ui(session_dir: Path, manager: ImageManager, images):
    """
    PowerPoint出力UI

    Args:
        session_dir: セッションディレクトリ
        manager: ImageManagerインスタンス
        images: ImageDataのリスト
    """
    st.subheader("📊 PowerPoint出力")

    col1, col2 = st.columns([3, 1])

    with col1:
        # タイトル入力
        title = st.text_input(
            "プレゼンテーションのタイトル",
            value="操作マニュアル",
            help="タイトルスライドに表示されます"
        )

    with col2:
        st.write("")  # スペース調整
        st.write("")

    # 生成ボタン
    if st.button("📥 PowerPoint生成", type="primary", use_container_width=True):
        if len(images) == 0:
            st.error("画像がありません。PowerPointを生成できません。")
            return

        try:
            # 出力ファイル名
            output_filename = f"{session_dir.name}_manual.pptx"
            output_path = session_dir / output_filename

            # PowerPoint生成
            with st.spinner("PowerPointファイルを生成中..."):
                generator = PPTXGenerator()
                result_path = generator.generate(images, output_path, title=title)

            st.success(f"✅ PowerPointファイルを生成しました: `{output_filename}`")

            # ダウンロードボタン
            with open(result_path, "rb") as f:
                st.download_button(
                    label="💾 ダウンロード",
                    data=f,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ PowerPoint生成中にエラーが発生しました: {e}")


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
