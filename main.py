import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config import AppConfig
from editor_functions import EditorFunctions
from file_processor import FileProcessor


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