import glob
import os


class FileProcessor:

    def __init__(self):
        pass

    def get_all_files(self, current_dir):
        """フォルダー内の全ファイルをリストアップする"""
        if not current_dir:
            return []
        search_path = os.path.join(current_dir, "*")
        all_items = glob.glob(search_path)
        return [item for item in all_items if os.path.isfile(item)]

    def read_as_binary(self, full_path):
        """ファイルを16進数バイナリの行リストに変換する"""
        with open(full_path, "rb") as f:
            bindata = f.read()

        lines = []
        bytes_per_line = 16
        for i in range(0, len(bindata), bytes_per_line):
            chunk = bindata[i:i+bytes_per_line]
            hex_strings = [f"{b:02X}" for b in chunk]
            lines.append(" ".join(hex_strings))
        return lines

    def read_as_text(self, full_path, encoding):
        """ファイルをテキストとして読み込む"""
        with open(full_path, "r", encoding=encoding) as f:
            return f.readlines()

    def read_with_auto_detect(self, full_path):
        """文字コードを自動判別して読み込む（sjis -> utf-8 -> utf-16 -> binary）"""
        # 1. Shift-JIS チェック
        try:
            with open(full_path, "r", encoding="shift_jis") as f:
                return f.readlines(), "shift_jis"
        except UnicodeDecodeError:
            pass

        # 2. UTF-8 チェック
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.readlines(), "utf-8"
        except UnicodeDecodeError:
            pass

        # 3. UTF-16 チェック
        try:
            with open(full_path, "r", encoding="utf-16") as f:
                return f.readlines(), "utf-16"
        except UnicodeDecodeError:
            pass

        # 4. すべて失敗したらバイナリとして扱う
        return None, "binary"