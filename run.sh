#!/usr/bin/env bash
# Instala, compila a interface e sobe tudo em http://localhost:8000
cd "$(dirname "$0")"
PY=$(command -v python3.12 || command -v python3.11 || command -v python3)
[ -d .venv ] || $PY -m venv .venv || { echo "Falha ao criar o ambiente virtual (precisa de Python 3.11+)."; exit 1; }
. .venv/bin/activate
pip install -r backend/requirements.txt || { echo "Falha ao instalar as dependências Python."; exit 1; }
if [ ! -f frontend/dist/index.html ]; then
  command -v npm >/dev/null || { echo "Node.js/npm não encontrado: instale o Node 20+ (https://nodejs.org)."; exit 1; }
  (cd frontend && npm install --no-audit --no-fund && npm run build) || { echo "Falha ao compilar a interface."; exit 1; }
fi
python scripts/check_setup.py || exit 1
echo "Abra http://localhost:8000"
uvicorn app.main:app --app-dir backend --port 8000
