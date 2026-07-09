import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


class EditorClickActions:

    def __init__(self, funcs):
        """本体の機能管理（funcs）への参照を保持する"""
        self.funcs = funcs

    def select_folder(self):
        """「フォルダを選択」の処理"""
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return
        self.funcs.current_dir = folder_selected
        self.funcs.app.path_label.config(text=self.funcs.current_dir)
        self.update_file_list()

    def update_file_list(self):
        """「一覧更新」の処理"""
        if not self.funcs.current_dir or not os.path.exists(
            self.funcs.current_dir
        ):
            return
        self.funcs.app.file_listbox.delete(0, tk.END)
        try:
            files = sorted(os.listdir(self.funcs.current_dir))
            for f in files:
                if os.path.isfile(os.path.join(self.funcs.current_dir, f)):
                    self.funcs.app.file_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("エラー", f"一覧の取得に失敗:\n{e}")

    def insert_wrapped_text(self, text):
        """行番号と本文をそれぞれの専用枠に分けて綺麗に挿入する"""
        if not text:
            return

        # 行番号専用枠の制限を一時的に解除して綺麗に掃除する
        self.funcs.app.line_num_area.config(state=tk.NORMAL)
        self.funcs.app.line_num_area.delete("1.0", tk.END)

        w = self.funcs.wrap_chars
        # 元の文章の改行で1行ずつにばらす
        lines = text.splitlines()

        for idx, line in enumerate(lines, 1):
            if not line:
                # 空行の場合は行番号を入れ、本文側には改行のみ入れる
                self.funcs.app.line_num_area.insert(tk.END, f"{idx:04}:\n")
                self.funcs.app.text_area.insert(tk.END, "\n")
                continue

            # 1行を指定の桁数でぶつ切りにする
            chunks = [line[i : i + w] for i in range(0, len(line), w)]

            for chunk_idx, chunk in enumerate(chunks):
                if chunk_idx == 0:
                    # その行の本当の先頭だけに行番号を書き込む
                    self.funcs.app.line_num_area.insert(tk.END, f"{idx:04}:\n")
                else:
                    # 折り返された2行目以降は、行番号枠には改行のみを入れて高さを揃える
                    self.funcs.app.line_num_area.insert(tk.END, "\n")
                
                # 本文枠には余計な空白を混ぜず、純粋な文字データのみを挿入する
                self.funcs.app.text_area.insert(tk.END, f"{chunk}\n")

        # 入れ終わったら行番号専用枠を再び書き込み禁止にロックする
        self.funcs.app.line_num_area.config(state=tk.DISABLED)

    def search_keyword(self, start_idx, forward=True):
        """文字列検索の中心処理（次へ・前へ共通）"""
        word = self.funcs.app.search_entry.get()
        if not word:
            return start_idx

        self.funcs.app.text_area.tag_remove("match", "1.0", tk.END)
        
        if forward:
            idx = self.funcs.app.text_area.search(
                word, start_idx, stopindex=tk.END
            )
            if not idx:
                idx = self.funcs.app.text_area.search(word, "1.0", stopindex=tk.END)
        else:
            current = self.funcs.app.text_area.index(f"{start_idx}-{len(word)}c")
            idx = self.funcs.app.text_area.search(
                word, current, stopindex="1.0", backwards=True
            )
            if not idx:
                idx = self.funcs.app.text_area.search(
                    word, tk.END, stopindex="1.0", backwards=True
                )

        if idx:
            self.funcs.app.text_area.tag_add("match", idx, f"{idx}+{len(word)}c")
            self.funcs.app.text_area.tag_config(
                "match", background="yellow", foreground="black"
            )
            self.funcs.app.text_area.see(idx)
            return f"{idx}+{len(word)}c" if forward else idx
        else:
            messagebox.showinfo("検索結果", "見つかりませんでした。")
            return "1.0"

    def go_to_line(self):
        """入力された数値の行番号へ最上段にピタッと移動する処理"""
        line_str = self.funcs.app.search_entry.get().strip()
        if not line_str:
            messagebox.showwarning("警告", "行番号を入力してください。")
            return

        # 文字や記号などの入力に対する安全対策
        if not line_str.isdigit():
            messagebox.showwarning("注意", "行番号には正しい数値を入力してください。")
            return

        target_line = int(line_str)
        if target_line <= 0:
            messagebox.showwarning("注意", "行番号は1以上を指定してください。")
            return

        # 行番号の専用枠から「0002:」のような目的の表記を検索する
        search_target = f"{target_line:04}:"
        idx = self.funcs.app.line_num_area.search(search_target, "1.0", stopindex=tk.END)

        if idx:
            # 見つかった行の位置を取得し、最上段にピタッと表示させる
            line_num = idx.split(".")[0]
            self.funcs.app.text_area.yview(f"{line_num}.0")
        else:
            messagebox.showinfo("移動結果", f"指定された行番号 {target_line} は見つかりませんでした。")

    def clear_text_area(self):
        """「クリア」の処理"""
        # 本文枠の掃除
        self.funcs.app.text_area.config(state=tk.NORMAL)
        self.funcs.app.text_area.delete("1.0", tk.END)
        self.funcs.app.text_area.config(state=tk.DISABLED)
        
        # 行番号枠の掃除
        self.funcs.app.line_num_area.config(state=tk.NORMAL)
        self.funcs.app.line_num_area.delete("1.0", tk.END)
        self.funcs.app.line_num_area.config(state=tk.DISABLED)

        self.funcs.update_title("clear")
        self.funcs.last_opened_file = None
        self.funcs.search_current_index = "1.0"
        self.funcs.app.file_listbox.selection_clear(0, tk.END)

    def open_setting_dialog(self):
        """「設定変更」の処理"""
        try:
            subprocess.run(["python", "setting_dialog.py"])
            (
                saved_version,
                saved_dir,
                saved_wrap,
                saved_size,
                theme_list,
                editor_list,
            ) = self.funcs.app.config_manager.load_settings()

            # 新しく読み込んだ設定を変数にしっかり上書き
            self.funcs.version = saved_version
            self.funcs.wrap_chars = (
                int(saved_wrap) if str(saved_wrap).isdigit() else 25
            )
            self.funcs.font_size = (
                int(saved_size) if str(saved_size).isdigit() else 16
            )

            # 【新設】設定ファイルから新しく読み込まれた配色情報を確実に同期させます
            if theme_list:
                self.funcs.color_themes = theme_list
                if self.funcs.app.color_combo:
                    self.funcs.app.color_combo["values"] = [t[0] for t in theme_list]

            self.funcs.app.text_area.config(font=("Meiryo", self.funcs.font_size))
            self.funcs.app.line_num_area.config(font=("Meiryo", self.funcs.font_size))

            # 設定画面から戻ったタイミングで、題名欄の版番号表記も連動更新する
            if self.funcs.last_opened_file:
                file_name = os.path.basename(self.funcs.last_opened_file)
                self.funcs.display_file_content(
                    self.funcs.last_opened_file, file_name
                )
            else:
                # 書類を開いていない状態なら、すっきりした初期題名に同期
                self.update_title("clear")

        except Exception as e:
            messagebox.showerror("エラー", f"設定画面の起動に失敗:\n{e}")

    def open_with_notepad(self):
        """「外部編集機で開く」の処理"""
        if not self.funcs.last_opened_file:
            messagebox.showwarning(
                "警告", "開く書類が選択されていません。"
            )
            return

        # 選択されている外部編集機の経路を取得
        editor_path = getattr(self.funcs, "selected_editor_path", "notepad.exe")

        if editor_path == "notepad.exe" or not editor_path:
            exists = True
        else:
            exists = os.path.exists(editor_path) and not os.path.isdir(editor_path)

        if not exists:
            editor_path = "notepad.exe"

        try:
            subprocess.Popen([editor_path, self.funcs.last_opened_file])
        except Exception as e:
            messagebox.showerror(
                "エラー",
                f"編集機の起動に失敗しました:\n経路: {editor_path}\n原因: {e}",
            )