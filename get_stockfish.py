"""체스 컴퓨터 상대(Stockfish)를 engine/stockfish.exe로 내려받는다. 처음 한 번만 실행."""
import io
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://github.com/official-stockfish/Stockfish/releases/latest/download/"
       "stockfish-windows-x86-64-universal.zip")
TARGET = Path(__file__).parent / "engine" / "stockfish.exe"


def main():
    print("Stockfish 내려받는 중...", URL)
    data = urllib.request.urlopen(URL).read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        exe = next(n for n in z.namelist() if n.endswith(".exe"))
        TARGET.parent.mkdir(exist_ok=True)
        TARGET.write_bytes(z.read(exe))
    print("완료:", TARGET)


if __name__ == "__main__":
    main()
