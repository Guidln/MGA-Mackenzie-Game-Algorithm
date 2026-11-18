"""Diagnóstico: python scripts/check_setup.py  (mostra o que falta para rodar o MGA Discovery)."""
import importlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
ok = True


def passo(nome, cond, dica=""):
    global ok
    print(("[ok]   " if cond else "[ERRO] ") + nome + ("" if cond else "\n       -> " + dica))
    ok &= bool(cond)


passo(f"Python {sys.version_info.major}.{sys.version_info.minor} (precisa de 3.11 ou superior)", sys.version_info >= (3, 11), "Instale Python 3.11+.")
for m in ("fastapi", "uvicorn", "pandas", "numpy", "sklearn", "openpyxl", "pydantic"):
    try:
        importlib.import_module(m); passo(f"pacote {m}", True)
    except ImportError:
        passo(f"pacote {m}", False, "pip install -r backend/requirements.txt")
from app.core import config  # noqa: E402

passo(f"base de jogos em {config.DATA_PATH}", config.DATA_PATH.exists(),
      "Copie a planilha (a que tem a aba Base_Jogos) para backend/data/. Qualquer nome .xlsx serve.")
passo(f"planilha de resultados em {config.RESULTS_PATH}", config.RESULTS_PATH.exists(), "Arquivo MGA_Resultados_*.xlsx deve ficar em backend/data/.")
if config.DATA_PATH.exists():
    try:
        from app.services.engine import Engine
        e = Engine()
        passo(f"base carregada: {e.df.shape[0]} jogos, matriz {e.X.shape[0]} x {e.X.shape[1]}", True)
        passo("matriz esperada 66 x 34", e.X.shape == (66, 34), "A base difere da usada no relatório; os indicadores da planilha de resultados não valerão para ela.")
    except Exception as ex:
        passo("leitura da base e construção da matriz", False, f"{type(ex).__name__}: {ex}")
passo("interface compilada (frontend/dist)", (ROOT / "frontend" / "dist" / "index.html").exists(), "cd frontend && npm install && npm run build  (ou use npm run dev)")
print("\nTudo certo." if ok else "\nCorrija os itens [ERRO] acima e rode de novo.")
sys.exit(0 if ok else 1)
