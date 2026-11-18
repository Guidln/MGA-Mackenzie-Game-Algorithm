"""Baixa a capa de TODOS os jogos da base (via Wikipédia) para backend/data/covers/ e gera backend/data/covers.json.
Rode uma vez, com internet:  python scripts/fetch_covers.py   (depois reinicie a API; as capas passam a ser servidas em /covers/*)."""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core import config  # noqa: E402
import pandas as pd  # noqa: E402

API = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=thumbnail&pithumbsize=500&redirects=1"
UA = {"User-Agent": "MGA-Discovery/1.0 (projeto academico; contato: Mackenzie)"}
PAGES = json.loads((ROOT / "frontend/src/lib/coverPages.json").read_text(encoding="utf-8"))
OUT = config.DATA_DIR / "covers"; OUT.mkdir(exist_ok=True)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def thumb(url):
    pages = json.loads(get(url)).get("query", {}).get("pages", {})
    return next(iter(pages.values()), {}).get("thumbnail", {}).get("source")


def find(title):
    t = title.replace("’", "'")
    return (thumb(f"{API}&titles={urllib.parse.quote(PAGES.get(title, t))}")
            or thumb(f"{API}&generator=search&gsrlimit=1&gsrsearch={urllib.parse.quote(t + ' video game')}"))


covers, faltam = {}, []
for jogo in pd.read_excel(config.DATA_PATH, sheet_name="Base_Jogos")["jogo"].dropna():
    try:
        url = find(jogo)
        if not url:
            faltam.append(jogo); continue
        nome = re.sub(r"[^a-z0-9]+", "-", jogo.lower()).strip("-") + ".jpg"
        (OUT / nome).write_bytes(get(url)); covers[jogo] = f"/covers/{nome}"
        print("ok ", jogo)
    except Exception as e:  # noqa: BLE001
        faltam.append(jogo); print("ERRO", jogo, e)
    time.sleep(0.3)
config.COVERS_PATH.write_text(json.dumps(covers, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{len(covers)} capas salvas. Sem capa: {faltam or 'nenhum'} (esses usam a capa tipográfica; adicione manualmente em covers.json).")
