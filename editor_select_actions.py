import os
import tkinter as tk
from tkinter import messagebox

# 互いに読み込み合うことによる不具合を防ぐため、この位置での引き込みは行いません。
# 司令塔（funcs）の情報は、初期化の際に受け取る self.funcs からすべて安全に参照できます。


class EditorSelectActions:

    def __init__(self, funcs):
        """本体の機能管理（funcs）への参照を保持する"""
        self.funcs = funcs
        # 起動時の初期の編集機として一覧の先頭（メモ帳）の経路を設定しておく
        if hasattr(self.funcs, "editor_list") and self.funcs.editor_list:
            self.funcs.selected_editor_path = self.funcs.editor_list[0][1]
        else:
            self.funcs.selected_editor_path = "notepad.exe"

    def change_theme_color(self, event=None):
        """選択箱で選ばれた配色の色を画面に適用する"""
        selected_idx = self.funcs.app.color_combo.current()
        if selected_idx == -1:
            return

        # 読み込まれている配色情報から背景色と文字色を抽出
        theme = self.funcs.color_themes[selected_idx]
        bg_color = theme[2]
        fg_color = theme[3]

        # 本文枠と一覧箱、および行番号枠の背景色を一斉に切り替える
        self.funcs.app.text_area.config(bg=bg_color, fg=fg_color)
        self.funcs.app.file_listbox.config(bg=bg_color, fg=fg_color)

        # 行番号枠の背景色も連動させ、文字色は見やすい灰色に整える
        self.funcs.app.line_num_area.config(bg=bg_color)
        self.funcs.app.text_area.tag_config("line_num", foreground="gray")

    def on_file_select(self, event=None):
        """一覧内のファイルがクリックされたとき、同じ書類でも必ず新しく読み直す"""
        selected_indices = self.funcs.app.file_listbox.curselection()
        if not selected_indices:
            return
        file_name = self.funcs.app.file_listbox.get(selected_indices[0])
        file_path = os.path.join(self.funcs.current_dir, file_name)

        # 同一の書類であっても処理を飛ばさず、毎回最新の状態で読み込み直す
        self.funcs.last_opened_file = file_path
        self.funcs.display_file_content(file_path, file_name)

    def change_editor_select(self, event=None):
        """外部編集機の選択箱が切り替えられたときに呼び出される処理"""
        # 画面側に外部編集機の選択箱（editor_combo）があるか確認
        if not hasattr(self.funcs.app, "editor_combo"):
            return

        # 選択箱で今何番目の項目が選ばれているかを取得
        selected_idx = self.funcs.app.editor_combo.current()
        if selected_idx == -1:
            return

        # 登録されている編集機一覧から、選ばれたものの実際の経路を抽出して上書きする
        try:
            if hasattr(self.funcs, "editor_list") and self.funcs.editor_list:
                editor_info = self.funcs.editor_list[selected_idx]
                # 選択された編集機の経路（例: C:\Program Files...\TeraPad.exe）を代入
                self.funcs.selected_editor_path = editor_info[1]
            else:
                self.funcs.selected_editor_path = "notepad.exe"
        except Exception as e:
            messagebox.showerror(
                "エラー", f"外部編集機の切り替えに失敗しました:\n{e}"
            )