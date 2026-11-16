import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"


def find_base():
    """Base de jogos: MGA_DATA_PATH, o nome padrão ou qualquer .xlsx em backend/data/ que tenha a aba Base_Jogos
    (aceita nomes como 'the_game_awards_2014_2024_ofc (1).xlsx')."""
    env = os.environ.get("MGA_DATA_PATH")
    if env:
        return Path(env)
    padrao = DATA_DIR / "the_game_awards_2014_2024_ofc.xlsx"
    if padrao.exists():
        return padrao
    try:
        import openpyxl
        for f in sorted(DATA_DIR.glob("*.xlsx")):
            if f.name.startswith(("~", "MGA_Resultados")):
                continue
            try:
                wb = openpyxl.load_workbook(f, read_only=True)
                ok = "Base_Jogos" in wb.sheetnames
                wb.close()
                if ok:
                    return f
            except Exception:
                continue
    except ImportError:
        pass
    return padrao


def find_results():
    env = os.environ.get("MGA_RESULTS_PATH")
    if env:
        return Path(env)
    for nome in ("MGA_Resultados_Etapa4.xlsx", "MGA_Resultados_Etapa3.xlsx"):
        if (DATA_DIR / nome).exists():
            return DATA_DIR / nome
    return DATA_DIR / "MGA_Resultados_Etapa3.xlsx"


DATA_PATH = find_base()
RESULTS_PATH = find_results()
COVERS_PATH = Path(os.environ.get("MGA_COVERS_PATH") or DATA_DIR / "covers.json")
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",") if o.strip()]
