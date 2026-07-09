import configparser
import os


class ConfigLoader:

    def __init__(self, ini_filename, read_filter_func):
        """iniファイル名と、//注釈を除去する関数をconfig本体から受け取る"""
        self.ini_filename = ini_filename
        self._read_without_double_slash = read_filter_func

    def execute_load(self):
        """settings.ini から設定を読み込み、各種変数に代入して返す処理を専門に行う"""
        # 色情報やエディタ情報の特殊な書き方に対応するため、値なしの行を許可して初期化します
        config = configparser.ConfigParser(
            comment_prefixes=("#", ";"), allow_no_value=True
        )

        # フィルター済みのテキストデータを取得
        ini_data = self._read_without_double_slash()

        # 起動時の初期値をここで一括設定
        version = "0.07.06"
        current_dir = ""
        wrap_num = "25"
        font_size = "16"
        theme_list = []  # ← ここに解析した色情報を格納していきます
        editor_list = []  # 【新設】ここに解析した外部編集機の情報を格納していきます

        # データがあれば解析して変数に代入
        if ini_data:
            try:
                config.read_string(ini_data)

                # [App] 区分から版番号を取得
                if "App" in config:
                    version = config["App"].get("version", "0.07.06")

                if "Settings" in config:
                    current_dir = config["Settings"].get("current_dir", "")
                    wrap_num = config["Settings"].get("wrap_num", "25")
                    font_size = config["Settings"].get("font_size", "16")
            except Exception:
                pass

            # [Color_Theme] 区分の手動解析処理（安全対策完備）
            try:
                in_color_theme = False
                for line in ini_data.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    # 区分の切り替わりを監視します
                    if line.startswith("[") and line.endswith("]"):
                        if line == "[Color_Theme]":
                            in_color_theme = True
                        else:
                            in_color_theme = False
                        continue

                    # 色情報区分のなかにいる場合、1行ずつ細かく分解します
                    if in_color_theme:
                        parts = [p.strip().strip('"') for p in line.split(",")]
                        if len(parts) >= 4:
                            theme_name = parts[2]
                            theme_id = f"{parts[0]}_{parts[1]}"

                            # カンマの打ち忘れ対策（空白で区切られていても色を抽出できるようにします）
                            color_parts = []
                            for p in parts[3:]:
                                color_parts.extend(p.split())

                            # 背景色と文字色の2つが揃っていれば一覧に追加します
                            if len(color_parts) >= 2:
                                bg_color = color_parts[0]
                                fg_color = color_parts[1]
                                theme_list.append(
                                    [theme_name, theme_id, bg_color, fg_color]
                                )
            except Exception:
                pass

            # 【新設】[Editor_Data] 区分の手動解析処理（安全対策完備）
            try:
                in_editor_data = False
                for line in ini_data.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    # 区分の切り替わりを監視します
                    if line.startswith("[") and line.endswith("]"):
                        if line == "[Editor_Data]":
                            in_editor_data = True
                        else:
                            in_editor_data = False
                        continue

                    # エディタ情報区分のなかにいる場合、1行ずつ細かく分解します
                    if in_editor_data:
                        parts = [p.strip().strip('"') for p in line.split(",")]
                        if len(parts) >= 4:
                            editor_name = parts[2]
                            editor_path = parts[3]
                            # 名前と実際の経路の組を一覧に追加します
                            editor_list.append([editor_name, editor_path])
            except Exception:
                pass

        # もし設定ファイルから色がうまく読めなかった場合の保険用初期値
        if not theme_list:
            theme_list = [["白背景", "C_Theme_1", "#ffffff", "#000000"]]

        # 【新設】もし設定ファイルからエディタがうまく読めなかった場合の保険用初期値
        if not editor_list:
            editor_list = [["メモ帳", "C:\\Windows\\System32\\notepad.exe"]]

        # 代入した変数と、用意した一覧をまとめて返します
        return (
            version,
            current_dir,
            wrap_num,
            font_size,
            theme_list,
            editor_list,
        )