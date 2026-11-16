@echo off
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r backend\requirements.txt || (echo Falha ao instalar as dependencias Python. & exit /b 1)
if not exist frontend\dist\index.html (
  where npm >nul 2>nul || (echo Node.js/npm nao encontrado: instale o Node 20+ & exit /b 1)
  pushd frontend
  call npm install --no-audit --no-fund
  call npm run build || (echo Falha ao compilar a interface. & popd & exit /b 1)
  popd
)
python scripts\check_setup.py || exit /b 1
echo Abra http://localhost:8000
uvicorn app.main:app --app-dir backend --port 8000
