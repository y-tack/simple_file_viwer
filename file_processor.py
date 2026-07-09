import os

class FileProcessor:
    def read_with_auto_detect(self, file_path):
        if self._is_binary_file(file_path): return None, "binary"
        encodings = ["utf-8", "cp932", "utf-16"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.readlines(), enc
            except (UnicodeDecodeError, SyntaxError): continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.readlines(), "utf-8"
        except Exception: return [], "utf-8"

    def read_as_text(self, file_path, encoding):
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            return f.readlines()

    def read_as_binary(self, file_path):
        hex_lines = []
        try:
            with open(file_path, "rb") as f:
                offset = 0
                while True:
                    chunk = f.read(16)
                    if not chunk: break
                    hex_dump = " ".join(f"{b:02x}" for b in chunk)
                    if len(chunk) < 16: hex_dump = hex_dump.ljust(47)
                    ascii_dump = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                    hex_lines.append(f"{offset:08x}:  {hex_dump}  |{ascii_dump}|")
                    offset += 16
        except Exception as e: hex_lines.append(f"解析エラー: {e}")
        return hex_lines

    def _is_binary_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                return b"\x00" in f.read(4096)
        except Exception: return False