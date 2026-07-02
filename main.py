import tkinter as tk

from config import AppConfig
from editor_functions import EditorFunctions


class SimpleEditorApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("シンプルファイル閲覧機（モジュール分割版）")
        self.root.geometry("950x650")

        # 設定と機能を読み込んで合体
        self.config = AppConfig()
        self.funcs = EditorFunctions(self)

        # --- 最上部エリア ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        folder_frame = tk.Frame(top_frame)
        folder_frame.pack(fill=tk.X, pady=2)

        folder_button = tk.Button(
            folder_frame, text="フォルダーを選択する", font=self.config.default_font, command=self.funcs.select_folder
        )
        folder_button.pack(side=tk.LEFT, padx=5)

        self.folder_label = tk.Label(
            folder_frame, text="選択中: （フォルダー未選択）", font=self.config.default_font, fg="gray"
        )
        self.folder_label.pack(side=tk.LEFT, padx=5)

        encoding_frame = tk.Frame(top_frame)
        encoding_frame.pack(fill=tk.X, pady=2)

        encoding_label = tk.Label(encoding_frame, text="モード/文字コード:", font=self.config.default_font)
        encoding_label.pack(side=tk.LEFT, padx=5)

        self.encoding_var = tk.StringVar(value="auto")
        modes = [
            ("自動判別", "auto"),
            ("UTF-8", "utf-8"),
            ("UTF-16", "utf-16"),
            ("Shift-JIS", "shift_jis"),
            ("16進数バイナリ", "binary")
        ]
        for text, val in modes:
            rb = tk.Radiobutton(
                encoding_frame, text=text, font=self.config.default_font,
                variable=self.encoding_var, value=val, command=self.funcs.on_file_select
            )
            rb.pack(side=tk.LEFT, padx=5)

        # --- メインエリア（左右分割） ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左側：ファイル一覧エリア
        left_frame = tk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)

        # ★【バグ修正】消えていたボタン類を左側フレームの上部に正しく配置
        refresh_button = tk.Button(
            left_frame, text="一覧を更新する", font=self.config.default_font, command=self.funcs.load_file_list
        )
        refresh_button.pack(fill=tk.X, pady=2)

        clear_button = tk.Button(
            left_frame, text="テキスト表示をクリア", font=self.config.default_font, command=self.funcs.clear_text_area
        )
        clear_button.pack(fill=tk.X, pady=2)

        # リストボックス本体とスクロールバー
        list_scrollbar = tk.Scrollbar(left_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            left_frame, font=self.config.default_font, yscrollcommand=list_scrollbar.set
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        list_scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.bind("<<ListboxSelect>>", self.funcs.on_file_select)
        self.file_listbox.bind("<ButtonRelease-1>", self.funcs.on_file_select)

        # 右側：検索・各種設定ボタンとテキストエリア
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        search_frame = tk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(search_frame, text="検索:", font=self.config.default_font).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=15, font=self.config.default_font)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.funcs.search_next)
        
        tk.Button(search_frame, text="検索", font=self.config.default_font, command=self.funcs.search_text).pack(side=tk.LEFT, padx=2)
        tk.Button(search_frame, text="前へ", font=self.config.default_font, command=self.funcs.search_prev).pack(side=tk.LEFT, padx=2)
        tk.Button(search_frame, text="次へ", font=self.config.default_font, command=self.funcs.search_next).pack(side=tk.LEFT, padx=2)

        tk.Button(search_frame, text="桁数を変更", font=self.config.default_font, command=self.funcs.change_wrap_dialog
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(search_frame, text="文字サイズを変更", font=self.config.default_font, command=self.funcs.change_font_size_dialog
        ).pack(side=tk.LEFT, padx=2)

        text_scrollbar = tk.Scrollbar(right_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area = tk.Text(
            right_frame, font=self.config.text_font, wrap=tk.NONE, yscrollcommand=text_scrollbar.set
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_area.yview)

        # --- 最下部エリア（行移動） ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(bottom_frame, text="行移動:", font=self.config.default_font).pack(side=tk.LEFT, padx=5)
        self.line_entry = tk.Entry(bottom_frame, width=8, font=self.config.default_font)
        self.line_entry.pack(side=tk.LEFT, padx=5)
        self.line_entry.bind("<Return>", self.funcs.go_to_line)
        tk.Button(bottom_frame, text="移動", font=self.config.default_font, command=self.funcs.go_to_line).pack(side=tk.LEFT, padx=5)

        # 装飾タグを適用
        self.config.setup_tags(self.text_area)
        self.funcs.load_file_list()

        # アプリ終了時に設定を自動保存
        self.root.protocol("WM_DELETE_WINDOW", lambda: [self.funcs.save_current_settings(), self.root.destroy()])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SimpleEditorApp()
    app.run()
