@echo off
echo ========================================
echo  Video Transcription Platform - Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Iniciando servidor frontend...
echo  URL: http://localhost:3000
echo ========================================
echo.
echo IMPORTANTE:
echo 1. Asegurate de que el backend este ejecutandose
echo 2. Abre http://localhost:3000 en tu navegador
echo 3. Presiona Ctrl+C para detener el servidor
echo.

start http://localhost:3000

python -m http.server 3000

pause