import os
import tkinter as tk
from tkinter import messagebox

from editor_click_actions import EditorClickActions
from editor_select_actions import EditorSelectActions


class EditorFunctions:

    def __init__(
        self,
        app,
        processor,
        version,
        saved_wrap,
        saved_size,
        theme_list,
        editor_list,
    ):
        """引数の3番目に版番号を追加して受け取る"""
        self.app = app
        self.processor = processor
        self.version = version  # 読み込んだ版番号を保持
        self.current_dir = ""
        self.last_opened_file = None
        self.search_current_index = "1.0"

        self.wrap_chars = int(saved_wrap) if str(saved_wrap).isdigit() else 25
        self.font_size = int(saved_size) if str(saved_size).isdigit() else 16

        # 設定ファイルから読み込んだ配色一覧を代入（不具合時の保険付き）
        self.color_themes = (
            theme_list
            if theme_list
            else [["白背景", "white_bg", "#ffffff", "#000000"]]
        )
        self.editor_list = editor_list

        # 各種動作を司る部品の準備
        self.click_actions = EditorClickActions(self)
        self.select_actions = EditorSelectActions(self)

        # 起動時に選択箱へ配色一覧を設定
        if self.app.color_combo:
            self.app.color_combo["values"] = [t[0] for t in self.color_themes]
            self.app.color_combo.current(0)

    def update_title(self, status_type="default", file_name=None, info=None):
        """題名欄の表記を一括管理して書き換える関数"""
        # 常に最新の self.version を参照して表示します
        base_title = f"ファイル閲覧機 EasyViewer Ver {self.version}"

        if status_type == "binary":
            self.app.root.title(
                f"{base_title} - 16進数表記（自動判定） - {file_name}"
            )
        elif status_type == "text":
            self.app.root.title(
                f"{base_title} - ファイル閲覧（自動判定: {info}） - {file_name}"
            )
        elif status_type == "clear":
            self.app.root.title(base_title)
        else:
            self.app.root.title(base_title)

    def display_file_content(self, file_path, file_name):
        """ファイルの中身を自動判別して本文枠に表示する（中心処理）"""
        lines, enc_or_bin = self.processor.read_with_auto_detect(file_path)

        # 題名欄の書き換え処理を一括管理関数（update_title）に任せる
        if enc_or_bin == "binary":
            self.update_title("binary", file_name=file_name)
            lines = self.processor.read_as_binary(file_path)
        else:
            self.update_title("text", file_name=file_name, info=enc_or_bin)
            lines = self.processor.read_as_text(file_path, enc_or_bin)

        self.app.text_area.config(state=tk.NORMAL)
        self.app.text_area.delete("1.0", tk.END)

        if enc_or_bin == "binary":
            for line in lines:
                self.app.text_area.insert(tk.END, line + "\n")
        else:
            # 文字データの場合は設定された桁数で自動で折り返して挿入
            full_text = "".join(lines)
            self.click_actions.insert_wrapped_text(full_text)

        self.app.text_area.config(state=tk.DISABLED)
        self.search_current_index = "1.0"

    def search_next(self):
        """「次へ」ボタンの処理：次の該当箇所を強調表示"""
        self.search_current_index = self.click_actions.search_keyword(
            self.search_current_index, forward=True
        )

    def search_prev(self):
        """「前へ」ボタンの処理：前の該当箇所を強調表示"""
        self.search_current_index = self.click_actions.search_keyword(
            self.search_current_index, forward=False
        )