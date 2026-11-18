@echo off
setlocal EnableExtensions
title MGA Discovery - Inicializacao
cd /d "%~dp0"

echo.
echo ==========================================================
echo                 MGA DISCOVERY
echo             Inicializador para Windows
echo ==========================================================
echo Pasta: %CD%
echo.

if not exist "backend\app\main.py" (
  echo [ERRO] Pasta incorreta. Este BAT precisa ficar na raiz de mga-discovery.
  goto :falha
)
if not exist "frontend\package.json" (
  echo [ERRO] Nao encontrei frontend\package.json.
  goto :falha
)
if not exist "backend\requirements.txt" (
  echo [ERRO] Nao encontrei backend\requirements.txt.
  goto :falha
)

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado.
  echo Instale Python 3.11 ou superior e marque "Add Python to PATH".
  echo https://www.python.org/downloads/
  goto :falha
)

python -c "import sys; print('Python',sys.version.split()[0]); sys.exit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo [ERRO] O MGA exige Python 3.11 ou superior.
  goto :falha
)

where node >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Node.js nao encontrado. Instale Node.js LTS 20 ou superior.
  echo https://nodejs.org/en/download
  goto :falha
)
where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [ERRO] npm nao encontrado. Reinstale o Node.js LTS.
  goto :falha
)

echo.
echo [1/5] Preparando ambiente Python...
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 (
    echo [ERRO] Nao foi possivel criar o ambiente virtual.
    goto :falha
  )
)

echo.
echo [2/5] Instalando dependencias Python...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :falha
".venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
if errorlevel 1 (
  echo [ERRO] Falha ao instalar dependencias Python.
  goto :falha
)

echo.
echo [3/5] Instalando e compilando o frontend...
if not exist "frontend\dist\index.html" (
  pushd frontend
  call npm.cmd install --no-audit --no-fund
  if errorlevel 1 (
    popd
    echo [ERRO] Falha no npm install.
    goto :falha
  )
  call npm.cmd run build
  if errorlevel 1 (
    popd
    echo [ERRO] Falha no npm run build.
    goto :falha
  )
  popd
) else (
  echo Frontend ja compilado. Pulando instalacao e build.
)

echo.
echo [4/5] Verificando configuracao e arquivos de dados...
".venv\Scripts\python.exe" "scripts\check_setup.py"
if errorlevel 1 (
  echo.
  echo [ERRO] O diagnostico encontrou pendencias.
  echo Consulte a mensagem acima. A base original deve conter a aba Base_Jogos.
  goto :falha
)

echo.
echo [5/5] Iniciando servidor...
echo.
echo MGA Discovery: http://localhost:8000
echo Documentacao da API: http://localhost:8000/docs
echo Para encerrar, pressione CTRL+C.
echo.
".venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
echo.
echo O servidor foi encerrado.
goto :fim

:falha
echo.
echo ==========================================================
echo A INICIALIZACAO NAO FOI CONCLUIDA.
echo A janela ficara aberta para voce ler o erro.
echo ==========================================================
pause
exit /b 1

:fim
pause
endlocal
