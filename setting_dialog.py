import configparser
import os
import tkinter as tk
from tkinter import messagebox, simpledialog


class SettingDialogApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("設定変更サブプログラム")
        self.root.geometry("380x250")

        self.ini_filename = "settings.ini"

        # 初期値のデフォルト
        self.font_size = 16
        self.wrap_num = 25

        # 起動時にiniファイルから現在の設定をまとめて読み込む
        self.load_settings()

        # 状態表示用のラベル（サイズと桁数を並べて表示）
        self.status_label = tk.Label(
            self.root,
            text=f"【現在の設定】\n文字サイズ: {self.font_size} pt  /  折り返し: {self.wrap_num} 文字",
            font=("Meiryo", 11),
            justify=tk.CENTER,
        )
        self.status_label.pack(pady=20)

        # ボタン1：文字サイズを変更する
        btn_size = tk.Button(
            self.root,
            text="① 文字サイズを変更",
            font=("Meiryo", 11),
            width=22,
            command=self.change_font_size_dialog,
        )
        btn_size.pack(pady=5)

        # ボタン2：折り返し桁数を変更する
        btn_wrap = tk.Button(
            self.root,
            text="② 折り返し桁数を変更",
            font=("Meiryo", 11),
            width=22,
            command=self.change_wrap_num_dialog,
        )
        btn_wrap.pack(pady=5)

    def _read_without_double_slash(self):
        """ファイルから読み込み、//以降のコメントを除去したテキストデータを返す"""
        cleaned_lines = []
        if os.path.exists(self.ini_filename):
            try:
                with open(self.ini_filename, "r", encoding="utf-8") as f:
                    for line in f:
                        # 行の中に // があれば、それ以降をバッサリ切り捨てる
                        if "//" in line:
                            line = line.split("//")[0] + "\n"
                        cleaned_lines.append(line)
            except Exception:
                pass
        return "".join(cleaned_lines)

    def load_settings(self):
        """settings.ini から現在の設定を読み込む（//コメント対応版）"""
        config = configparser.ConfigParser(comment_prefixes=("#", ";"))

        # ファイルを直接読まず、//を除去したテキストデータを読み込ませる
        ini_data = self._read_without_double_slash()

        if ini_data:
            try:
                config.read_string(ini_data)
                if "Settings" in config:
                    saved_size = config["Settings"].get("font_size", "16")
                    saved_wrap = config["Settings"].get("wrap_num", "25")

                    if saved_size.isdigit():
                        self.font_size = int(saved_size)
                    if saved_wrap.isdigit():
                        self.wrap_num = int(saved_wrap)
            except Exception:
                pass

    def save_settings(self):
        """settings.ini へ現在の設定をまとめて書き込む"""
        config = configparser.ConfigParser(comment_prefixes=("#", ";"))

        # 保存時も一度 // を除去した状態で既存データをパースする
        ini_data = self._read_without_double_slash()
        if ini_data:
            try:
                config.read_string(ini_data)
            except Exception:
                pass

        if "Settings" not in config:
            config["Settings"] = {}

        config["Settings"]["font_size"] = str(self.font_size)
        config["Settings"]["wrap_num"] = str(self.wrap_num)

        try:
            with open(self.ini_filename, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました:\n{e}")

    def update_status_label(self):
        """画面のラベル表示を最新の状態に更新する"""
        self.status_label.config(
            text=f"【現在の設定】\n文字サイズ: {self.font_size} pt  /  折り返し: {self.wrap_num} 文字"
        )

    def change_font_size_dialog(self):
        """数値入力ダイアログを表示して文字サイズを更新・保存する"""
        new_size = simpledialog.askinteger(
            "文字サイズの変更",
            "文字サイズを入力してください (10?40):",
            initialvalue=self.font_size,
            minvalue=10,
            maxvalue=40,
        )

        if new_size is not None:
            self.font_size = new_size
            self.update_status_label()
            self.save_settings()
            messagebox.showinfo("完了", "文字サイズを保存しました！")

    def change_wrap_num_dialog(self):
        """数値入力ダイアログを表示して折り返し桁数を更新・保存する"""
        new_wrap = simpledialog.askinteger(
            "折り返し設定",
            "1行の折り返し桁数を入力してください (1?200):",
            initialvalue=self.wrap_num,
            minvalue=1,
            maxvalue=200,
        )

        if new_wrap is not None:
            self.wrap_num = new_wrap
            self.update_status_label()
            self.save_settings()
            messagebox.showinfo("完了", "折り返し桁数を保存しました！")


if __name__ == "__main__":
    app = SettingDialogApp()
    app.root.mainloop()