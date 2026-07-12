import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config import AppConfig
from editor_functions import EditorFunctions
from file_processor import FileProcessor


class SettingDialog:
    """大元の画面の上に重ねて表示する、設定変更専用の小さな画面クラス"""

    def __init__(self, parent, funcs):
        self.parent = parent
        self.funcs = funcs

        # 親画面（大元）の真上に新しい窓を作成します
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("設定変更")
        self.dialog.geometry("350x250")
        
        # 設定画面が開いている間、大元の画面の操作を受け付けないように固定します
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 画面内の文字や枠の配置
        label_title = tk.Label(self.dialog, text="◆ 環境設定の変更 ◆", font=("Meiryo", 11, "bold"))
        label_title.pack(pady=10)

        # ① 文字の大きさ変更用の外枠
        frame_size = tk.LabelFrame(self.dialog, text="① 文字の大きさ変更", font=("Meiryo", 9), padx=10, pady=5)
        frame_size.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_size, text="数値(10-40):", font=("Meiryo", 9)).pack(side=tk.LEFT)
        self.entry_size = tk.Entry(frame_size, width=8, font=("Meiryo", 9))
        self.entry_size.insert(0, str(self.funcs.font_size))
        self.entry_size.pack(side=tk.LEFT, padx=5)

        btn_size_apply = tk.Button(frame_size, text="変更", font=("Meiryo", 9), command=self._apply_font_size)
        btn_size_apply.pack(side=tk.LEFT, padx=5)

        # ② 折り返し桁数変更用の外枠
        frame_wrap = tk.LabelFrame(self.dialog, text="② 折り返しの桁数変更", font=("Meiryo", 9), padx=10, pady=5)
        frame_wrap.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_wrap, text="桁数(1-200):", font=("Meiryo", 9)).pack(side=tk.LEFT)
        self.entry_wrap = tk.Entry(frame_wrap, width=8, font=("Meiryo", 9))
        self.entry_wrap.insert(0, str(self.funcs.wrap_chars))
        self.entry_wrap.pack(side=tk.LEFT, padx=5)

        btn_wrap_apply = tk.Button(frame_wrap, text="変更", font=("Meiryo", 9), command=self._apply_wrap_num)
        btn_wrap_apply.pack(side=tk.LEFT, padx=5)

        # 画面を閉じるためのボタン
        btn_close = tk.Button(self.dialog, text="設定画面を閉じる", font=("Meiryo", 10), command=self.dialog.destroy)
        btn_close.pack(pady=10)

    def _apply_font_size(self):
        """入力された数値を確かめ、文字の大きさを安全に変更して保存する"""
        val = self.entry_size.get().strip()
        if not val.isdigit():
            messagebox.showwarning("注意", "正しい数値を入力してください。")
            return
        
        size = int(val)
        if not (10 <= size <= 40):
            messagebox.showwarning("制限", "文字の大きさは 10 から 40 の間で指定してください。")
            return

        # 司令塔の数値を書き換えて設定ファイルへ保存します
        self.funcs.font_size = size
        self.funcs.app.config_manager.save_settings(
            self.funcs.current_dir, self.funcs.wrap_chars, self.funcs.font_size
        )
        # 即座に画面全体の文字の大きさを書き換えます
        self.funcs.app.text_area.config(font=("Meiryo", size))
        self.funcs.app.line_num_area.config(font=("Meiryo", size))
        messagebox.showinfo("成功", f"文字の大きさを {size} に変更しました。")

    def _apply_wrap_num(self):
        """入力された数値を確かめ、折り返し桁数を安全に変更して保存する"""
        val = self.entry_wrap.get().strip()
        if not val.isdigit():
            messagebox.showwarning("注意", "正しい数値を入力してください。")
            return
        
        wrap = int(val)
        if not (1 <= wrap <= 200):
            messagebox.showwarning("制限", "折り返し桁数は 1 から 200 の間で指定してください。")
            return

        # 司令塔の数値を書き換えて設定ファイルへ保存します
        self.funcs.wrap_chars = wrap
        self.funcs.app.config_manager.save_settings(
            self.funcs.current_dir, self.funcs.wrap_chars, self.funcs.font_size
        )
        
        # 画面に文章が開かれている場合は、新しい桁数で綺麗に再配置します
        if self.funcs.last_opened_file:
            file_name = os.path.basename(self.funcs.last_opened_file)
            self.funcs.display_file_content(self.funcs.last_opened_file, file_name)
        
        messagebox.showinfo("成功", f"折り返し桁数を {wrap}文字 に変更しました。")


class EasyViewerApp:

    def __init__(self):
        self.root = tk.Tk()

        self.config_manager = AppConfig()
        (
            saved_version,
            saved_dir,
            saved_wrap,
            saved_size,
            theme_list,
            editor_list,
        ) = self.config_manager.load_settings()

        self.root.title(f"ファイル閲覧機 EasyViewer Ver {saved_version}")
        self.root.geometry("1050x650")

        self.processor = FileProcessor()

        # 操作用のボタンなどを配置する上部の枠
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        dir_frame = tk.Frame(top_frame)
        dir_frame.pack(fill=tk.X, pady=2)

        self.btn_select_dir = tk.Button(
            dir_frame, text="フォルダーを選択", font=("Meiryo", 10)
        )
        self.btn_select_dir.pack(side=tk.LEFT, padx=5)

        self.path_label = tk.Label(
            dir_frame, text="選択されていません", font=("Meiryo", 10), fg="gray"
        )
        self.path_label.pack(side=tk.LEFT, padx=5)

        ctrl_frame = tk.Frame(top_frame)
        ctrl_frame.pack(fill=tk.X, pady=2)

        tk.Label(ctrl_frame, text="検索:", font=("Meiryo", 10)).pack(
            side=tk.LEFT, padx=2
        )
        self.search_entry = tk.Entry(ctrl_frame, width=15, font=("Meiryo", 10))
        self.search_entry.pack(side=tk.LEFT, padx=2)

        self.btn_prev = tk.Button(ctrl_frame, text="前へ", font=("Meiryo", 10))
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(ctrl_frame, text="次へ", font=("Meiryo", 10))
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # 検索の入力欄に入れた数値の行へ移動するボタン
        self.btn_go_to_line = tk.Button(ctrl_frame, text="行番号へ", font=("Meiryo", 10))
        self.btn_go_to_line.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(
            ctrl_frame, text="一覧更新", font=("Meiryo", 10)
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_clear = tk.Button(
            ctrl_frame, text="クリア", font=("Meiryo", 10)
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # 外部の編集機を選ぶ選択箱
        self.editor_combo = ttk.Combobox(
            ctrl_frame, font=("Meiryo", 10), state="readonly", width=15
        )
        self.editor_combo.pack(side=tk.LEFT, padx=5)

        self.btn_notepad = tk.Button(
            ctrl_frame, text="外部エディタで開く", font=("Meiryo", 10)
        )
        self.btn_notepad.pack(side=tk.LEFT, padx=5)

        # 背景色（配色テーマ）を選ぶ選択箱
        self.color_combo = ttk.Combobox(
            ctrl_frame, font=("Meiryo", 10), state="readonly", width=15
        )
        self.color_combo.pack(side=tk.LEFT, padx=5)

        self.btn_settings = tk.Button(
            ctrl_frame, text="設定変更", font=("Meiryo", 10)
        )
        self.btn_settings.pack(side=tk.LEFT, padx=5)

        # 主要な表示枠（左側に一覧、右側に本文）
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左側：ファイルの一覧箱
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            width=28,
            font=("Meiryo", 10),
            yscrollcommand=list_scroll.set,
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.Y)
        list_scroll.config(command=self.file_listbox.yview)

        # 右側：本文の表示欄（行番号枠と本文枠の二つに分離）
        text_frame = tk.Frame(main_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_scroll = tk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ① 行番号専用の表示枠（幅は6文字分、最初は編集不可に設定）
        init_size = int(saved_size) if str(saved_size).isdigit() else 16
        self.line_num_area = tk.Text(
            text_frame,
            width=6,
            wrap=tk.NONE,
            font=("Meiryo", init_size),
            bg="#f3f4f6",
            fg="gray",
            state=tk.DISABLED,
        )
        self.line_num_area.pack(side=tk.LEFT, fill=tk.Y)

        # ② 本文専用の表示枠
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            undo=True,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 二つの枠の上下の動きをピッタリ同期させるための仕組み
        def sync_scroll(*args):
            self.line_num_area.yview(*args)
            self.text_area.yview(*args)

        def on_text_scroll(*args):
            text_scroll.set(*args)
            self.line_num_area.yview_moveto(args[0])

        text_scroll.config(command=sync_scroll)
        self.text_area.config(yscrollcommand=on_text_scroll)

        # 各機能を取り仕切る司令塔クラスの初期化
        self.funcs = EditorFunctions(
            self,
            self.processor,
            saved_version,
            saved_wrap,
            saved_size,
            theme_list,
            editor_list,
        )
        self.text_area.config(font=("Meiryo", self.funcs.font_size))
        self.line_num_area.config(font=("Meiryo", self.funcs.font_size))

        if editor_list:
            self.editor_combo["values"] = [editor[0] for editor in editor_list]
            self.editor_combo.current(0)
            self.funcs.selected_editor_path = editor_list[0][1]

        # 各種ボタンの動作紐付け
        self.btn_select_dir.config(
            command=self.funcs.click_actions.select_folder
        )
        self.btn_next.config(command=self.funcs.search_next)
        self.btn_prev.config(command=self.funcs.search_prev)
        self.btn_go_to_line.config(command=self.funcs.click_actions.go_to_line)
        self.btn_refresh.config(command=self.funcs.click_actions.update_file_list)
        self.btn_clear.config(command=self.funcs.click_actions.clear_text_area)
        self.btn_settings.config(
            command=self.funcs.click_actions.open_setting_dialog
        )
        self.btn_notepad.config(
            command=self.funcs.click_actions.open_with_notepad
        )

        # 選択箱や一覧箱の動作紐付け
        self.editor_combo.bind(
            "<<ComboboxSelected>>", self.funcs.select_actions.change_editor_select
        )
        self.color_combo.bind(
            "<<ComboboxSelected>>", self.funcs.select_actions.change_theme_color
        )
        self.file_listbox.bind(
            "<<ListboxSelect>>", self.funcs.select_actions.on_file_select
        )

        if saved_dir and os.path.exists(saved_dir):
            self.funcs.current_dir = saved_dir
            self.path_label.config(text=saved_dir)
            self.funcs.click_actions.update_file_list()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EasyViewerApp()
    app.run()