import configparser
import os
import tkinter as tk
from tkinter import font as tkfont


class AppConfig:

    def __init__(self):
        # フォント設定（サイズは初期値、後ほど読み込み値で上書きされます）
        self.default_font = tkfont.Font(family="Meiryo", size=11)
        self.text_font = tkfont.Font(family="Meiryo", size=16)
        self.h1_font = tkfont.Font(family="Meiryo", size=22, weight="bold")
        self.h2_font = tkfont.Font(family="Meiryo", size=18, weight="bold")

        # iniファイルのパス設定
        self.ini_filename = "settings.ini"

    def setup_tags(self, text_area):
        # テキストエリアの見た目（色やスタイル）のルール設定
        text_area.tag_config("number_blue", foreground="blue")
        text_area.tag_config("md_h1", font=self.h1_font, foreground="purple")
        text_area.tag_config("md_h2", font=self.h2_font, foreground="#555555")
        text_area.tag_config("md_quote", foreground="green")
        text_area.tag_config("search_match", background="yellow", foreground="black")

    def load_settings(self):
        """settings.ini から設定を読み込む（ファイルがなければ初期値を返す）"""
        config = configparser.ConfigParser()
        current_dir = ""
        wrap_num = "25"  # 初期値は25文字[cite: 5, 6]
        font_size = "16" # 初期値は16pt[cite: 5, 6]

        if os.path.exists(self.ini_filename):
            try:
                config.read(self.ini_filename, encoding="utf-8")
                if "Settings" in config:
                    current_dir = config["Settings"].get("current_dir", "")
                    wrap_num = config["Settings"].get("wrap_num", "25")
                    font_size = config["Settings"].get("font_size", "16")
            except Exception:
                pass
        return current_dir, wrap_num, font_size

    def save_settings(self, current_dir, wrap_num, font_size):
        """settings.ini へ現在の設定を保存する"""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "current_dir": current_dir,
            "wrap_num": wrap_num,
            "font_size": font_size
        }
        try:
            with open(self.ini_filename, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception:
            pass