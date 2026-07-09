import configparser
import os


class AppConfig:

    def __init__(self):
        # 設定を記憶しておく書類の名称
        self.ini_filename = "settings.ini"

    def _read_without_double_slash(self):
        """書類から読み込み、//以降の注釈を削り落とした文字データを返す"""
        cleaned_lines = []
        if os.path.exists(self.ini_filename):
            try:
                with open(self.ini_filename, "r", encoding="utf-8") as f:
                    for line in f:
                        if "//" in line:
                            line = line.split("//")[0] + "\n"
                        cleaned_lines.append(line)
            except Exception:
                pass
        return "".join(cleaned_lines)

    def load_settings(self):
        """設定の読み込み処理を専門の部品に丸投げして実行する"""
        # 互いに読み込み合うことによる不具合を防ぐため、ここで引き込みます
        from config_loader import ConfigLoader

        loader = ConfigLoader(
            self.ini_filename, self._read_without_double_slash
        )
        return loader.execute_load()

    def save_settings(self, current_dir, wrap_num, font_size):
        """現在の位置や数値を、既存の注釈や色情報の区分を壊さずに保存する"""
        # 色情報の特殊な記述を壊さずに読み込むため、値なしの行を許可して初期化します
        config = configparser.ConfigParser(
            comment_prefixes=("#", ";"), allow_no_value=True
        )

        ini_data = self._read_without_double_slash()
        if ini_data:
            try:
                config.read_string(ini_data)
            except Exception:
                pass

        # 設定保存時に [App] 区分と版番号が消えないように維持する
        if "App" not in config:
            config["App"] = {}
        if "version" not in config["App"]:
            config["App"]["version"] = "0.07.06"

        # [Settings] 区分がなければ新しく作成する
        if "Settings" not in config:
            config["Settings"] = {}

        # 現在の値を安全に代入する
        config["Settings"]["current_dir"] = current_dir
        config["Settings"]["wrap_num"] = str(wrap_num)
        config["Settings"]["font_size"] = str(font_size)

        try:
            with open(self.ini_filename, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception:
            pass