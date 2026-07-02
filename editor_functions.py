import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from file_processor import FileProcessor


class EditorFunctions:

    def __init__(self, app):
        self.app = app
        self.processor = FileProcessor()
        
        # 起動時にiniファイルから設定を読み込む
        self.current_dir, saved_wrap, saved_size = self.app.config.load_settings()
        self.last_opened_file = ""
        
        # 現在の折り返し桁数と文字サイズを記憶する変数
        self.wrap_chars = int(saved_wrap) if saved_wrap.isdigit() else 25
        self.font_size = int(saved_size) if saved_size.isdigit() else 16

        # 読み込んだ値を画面の部品とフォントに適用（起動直後に実行）
        self.app.root.after(10, self._apply_initial_settings)

    def _apply_initial_settings(self):
        """起動直後にインポートされた設定を画面の部品に適用する"""
        if self.current_dir:
            self.app.folder_label.config(text=f"選択中: {self.current_dir}")
            self.load_file_list()
        
        # フォントサイズを復元
        self.app.config.text_font.config(size=self.font_size)

    def save_current_settings(self):
        """現在の状態をiniファイルに保存する"""
        self.app.config.save_settings(self.current_dir, str(self.wrap_chars), str(self.font_size))

    def change_wrap_dialog(self):
        """ボタンが押されたら数字入力ダイアログを表示する（折り返し桁数）"""
        new_val = simpledialog.askinteger(
            "折り返し設定", 
            "1行の折り返し桁数を入力してください（1?200）：", 
            minvalue=1, 
            maxvalue=200, 
            initialvalue=self.wrap_chars
        )
        if new_val is not None:
            self.wrap_chars = new_val
            self.save_current_settings()
            if self.last_opened_file:
                self.on_file_select()

    def change_font_size_dialog(self):
        """ボタンが押されたら数字入力ダイアログを表示する（文字サイズ）"""
        new_size = simpledialog.askinteger(
            "文字サイズ設定", 
            "本文の文字サイズを入力してください（10?40pt）：", 
            minvalue=10, 
            maxvalue=40, 
            initialvalue=self.font_size
        )
        if new_size is not None:
            self.font_size = new_size
            # 画面上のフォントサイズを即座に変更
            self.app.config.text_font.config(size=self.font_size)
            self.save_current_settings()
            if self.last_opened_file:
                self.on_file_select()

    def select_folder(self):
        chosen_dir = filedialog.askdirectory()
        if chosen_dir:
            self.current_dir = chosen_dir
            self.app.folder_label.config(text=f"選択中: {self.current_dir}")
            self.load_file_list()
            self.save_current_settings()

    def load_file_list(self):
        self.app.file_listbox.delete(0, tk.END)
        if not self.current_dir:
            self.app.file_listbox.insert(tk.END, "（フォルダーを選んでください）")
            return

        files = self.processor.get_all_files(self.current_dir)
        if not files:
            self.app.file_listbox.insert(tk.END, "（対象ファイルがありません）")
            return

        files.sort()
        for f in files:
            self.app.file_listbox.insert(tk.END, os.path.basename(f))

    def on_file_select(self, event=None):
        selection = self.app.file_listbox.curselection()
        if not selection:
            if self.last_opened_file:
                file_name = self.last_opened_file
            else:
                return
        else:
            file_name = self.app.file_listbox.get(selection[0])
            if file_name in ["（フォルダーを選んでください）", "（対象ファイルがありません）"]:
                return
            self.last_opened_file = file_name

        full_path = os.path.join(self.current_dir, file_name)
        chosen_mode = self.app.encoding_var.get()
        self.app.text_area.delete("1.0", tk.END)
        display_line_count = 1

        max_chars = self.wrap_chars
        self.save_current_settings()

        raw_lines = None
        detected_mode = chosen_mode

        if chosen_mode == "auto":
            raw_lines, detected_mode = self.processor.read_with_auto_detect(full_path)

        if detected_mode == "binary" or chosen_mode == "binary":
            try:
                hex_lines = self.processor.read_as_binary(full_path)
                for hex_line in hex_lines:
                    self._insert_line_with_num(display_line_count, hex_line)
                    display_line_count += 1
                mode_caption = "自動判定: バイナリ" if chosen_mode == "auto" else "バイナリ"
                self.app.root.title(f"16進数バイナリ閲覧（{mode_caption}） - {file_name}")
                return
            except Exception as e:
                messagebox.showerror("エラー", f"バイナリ読み込み失敗:\n{e}")
                return

        try:
            if raw_lines is None:
                raw_lines = self.processor.read_as_text(full_path, detected_mode)

            for line in raw_lines:
                clean_line = line.rstrip("\n")
                if not clean_line:
                    self._insert_line_with_num(display_line_count, "")
                    display_line_count += 1
                    continue

                chunks = [clean_line[i:i+max_chars] for i in range(0, len(clean_line), max_chars)]
                for chunk in chunks:
                    self._insert_line_with_num(display_line_count, chunk, clean_line)
                    display_line_count += 1

            mode_caption = f"自動判定: {detected_mode.upper()}" if chosen_mode == "auto" else detected_mode.upper()
            self.app.root.title(f"ファイル閲覧（{mode_caption}） - {file_name}")
        except Exception as e:
            messagebox.showerror("エラー", f"読み込み失敗:\n{e}")

    def _insert_line_with_num(self, line_num, content, original_line=""):
        num_str = f"{line_num}: "
        s_num = self.app.text_area.index(tk.END + "-1c")
        self.app.text_area.insert(tk.END, num_str)
        e_num = self.app.text_area.index(tk.END + "-1c")
        self.app.text_area.tag_add("number_blue", s_num, e_num)

        s_txt = self.app.text_area.index(tk.END + "-1c")
        self.app.text_area.insert(tk.END, content + "\n")
        e_txt = self.app.text_area.index(tk.END + "-1c")

        ref_line = original_line if original_line else content
        if ref_line.startswith("# "):
            self.app.text_area.tag_add("md_h1", s_txt, e_txt)
        elif ref_line.startswith("## "):
            self.app.text_area.tag_add("md_h2", s_txt, e_txt)
        elif ref_line.startswith("> "):
            self.app.text_area.tag_add("md_quote", s_txt, e_txt)

    def go_to_line(self, event=None):
        line_num = self.app.line_entry.get()
        if not line_num.isdigit():
            messagebox.showwarning("注意", "半角数字で入力してください。")
            return
        target_index = f"{line_num}.0"
        try:
            self.app.text_area.yview(target_index)
            self.app.text_area.mark_set(tk.INSERT, target_index)
            self.app.text_area.focus_set()
        except Exception:
            pass

    def search_text(self):
        self.app.text_area.tag_remove("search_match", "1.0", tk.END)
        keyword = self.app.search_entry.get()
        if not keyword:
            return
        self._execute_search(keyword, "1.0", backwards=False)

    def search_next(self, event=None):
        """次へ検索（下に向かって検索）"""
        keyword = self.app.search_entry.get()
        if not keyword:
            return
        start_pos = self.app.text_area.index(tk.INSERT + "+1c")
        self._execute_search(keyword, start_pos, backwards=False)

    def search_prev(self, event=None):
        """前へ検索（上に向かって検索）"""
        keyword = self.app.search_entry.get()
        if not keyword:
            return
        start_pos = self.app.text_area.index(tk.INSERT + "-1c")
        self._execute_search(keyword, start_pos, backwards=True)

    def _execute_search(self, keyword, start_index, backwards=False):
        """検索の共通コア処理"""
        stop_pos = "1.0" if backwards else "end"
        pos = self.app.text_area.search(keyword, start_index, stopindex=stop_pos, backwards=backwards)
        
        if pos:
            self.app.text_area.tag_remove("search_match", "1.0", tk.END)
            end_pos = f"{pos}+{len(keyword)}c"
            self.app.text_area.tag_add("search_match", pos, end_pos)
            line_part = pos.split(".")[0]
            self.app.text_area.yview(f"{line_part}.0")
            self.app.text_area.mark_set(tk.INSERT, pos)
            self.app.text_area.focus_set()
        else:
            if start_index != "1.0" and not backwards:
                if messagebox.askyesno("検索終了", "先頭に戻って再検索しますか？"):
                    self.search_text()
            elif start_index != self.app.text_area.index(tk.END) and backwards:
                if messagebox.askyesno("検索終了", "末尾に戻って再検索しますか？"):
                    self.app.text_area.mark_set(tk.INSERT, tk.END)
                    self.search_prev()
            else:
                messagebox.showinfo("検索結果", "見つかりませんでした。")

    def clear_text_area(self):
        self.app.text_area.delete("1.0", tk.END)
        self.last_opened_file = ""
        self.app.file_listbox.selection_clear(0, tk.END)
        self.app.root.title("万能ファイル閲覧機（モジュール分割版）")