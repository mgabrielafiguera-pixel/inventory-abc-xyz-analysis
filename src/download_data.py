"""Descarga el dataset Online Retail II (UCI) y lo guarda en data/raw/.

Uso:
    python src/download_data.py
"""
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
XLSX_PATH = RAW_DIR / "online_retail_II.xlsx"


def download(force: bool = False) -> Path:
    """Descarga y descomprime el Excel si todavía no existe."""
    if XLSX_PATH.exists() and not force:
        print(f"Ya existe: {XLSX_PATH}")
        return XLSX_PATH

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Descargando Online Retail II desde UCI (~45 MB)...")
    with urllib.request.urlopen(URL) as resp:
        data = resp.read()

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".xlsx"))
        XLSX_PATH.write_bytes(zf.read(name))

    print(f"Guardado en: {XLSX_PATH}")
    return XLSX_PATH


if __name__ == "__main__":
    download()
