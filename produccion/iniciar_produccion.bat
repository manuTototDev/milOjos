@echo off
echo Iniciando Servidor Backend (FastAPI con Hot-Reload)...
start "Backend Mil Ojos" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Iniciando Servidor Frontend (Next.js)...
start "Frontend Mil Ojos" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Ambos servidores se han iniciado.
