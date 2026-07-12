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
        from config_loader import ConfigLoader

        loader = ConfigLoader(
            self.ini_filename, self._read_without_double_slash
        )
        return loader.execute_load()

    def save_settings(self, current_dir, wrap_num, font_size):
        """【改良】既存の特殊な色情報やエディタ情報を絶対に壊さずに、[Settings] のみ安全に上書きする"""
        lines = []
        if os.path.exists(self.ini_filename):
            try:
                with open(self.ini_filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                pass

        new_lines = []
        in_settings = False
        replaced = False

        for line in lines:
            stripped = line.strip()
            
            # 別の区分が始まったら設定区分の監視を終了する
            if stripped.startswith("[") and stripped.endswith("]"):
                if stripped == "[Settings]":
                    in_settings = True
                    new_lines.append(line)
                    # [Settings] の直後に新しい設定値を一括で書き出します
                    new_lines.append(f"current_dir = {current_dir}\n")
                    new_lines.append(f"wrap_num = {wrap_num}\n")
                    new_lines.append(f"font_size = {font_size}\n")
                    replaced = True
                    continue
                else:
                    in_settings = False

            # 設定区分のなかにいる間は、元の古い設定行（=を含む行）を無視して飛ばします
            if in_settings:
                if "=" in line:
                    continue
            
            new_lines.append(line)

        # もし書類のなかに [Settings] 区分がそもそも見つからなかった場合の安全装置
        if not replaced:
            new_lines.append("\n[Settings]\n")
            new_lines.append(f"current_dir = {current_dir}\n")
            new_lines.append(f"wrap_num = {wrap_num}\n")
            new_lines.append(f"font_size = {font_size}\n")

        try:
            with open(self.ini_filename, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass