@echo off
echo ========================================
echo  Video Transcription Platform - Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no esta instalado
    echo    Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [2/4] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: FFmpeg no esta instalado
    echo.
    echo FFmpeg es necesario para procesar videos.
    echo.
    echo ¿Quieres ejecutar el instalador de FFmpeg? (s/n)
    set /p choice="Respuesta: "
    if /i "%choice%"=="s" (
        cd /d "%~dp0"
        call install_ffmpeg.bat
        cd /d "%~dp0backend"
        echo.
        echo Verificando FFmpeg nuevamente...
        ffmpeg -version >nul 2>&1
        if errorlevel 1 (
            echo ❌ FFmpeg aun no esta disponible
            echo Por favor, instala FFmpeg manualmente y reinicia este script
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Por favor instala FFmpeg y reinicia este script:
        echo - Opcion 1: Ejecuta install_ffmpeg.bat
        echo - Opcion 2: choco install ffmpeg
        echo - Opcion 3: Descarga manual desde https://ffmpeg.org
        pause
        exit /b 1
    )
)
echo ✅ FFmpeg encontrado

echo.
echo [3/4] Configurando entorno virtual...
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Verificando dependencias...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias Python...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)
echo ✅ Dependencias verificadas

echo.
echo [4/4] Iniciando servidor backend...
echo.
echo ========================================
echo  🚀 SERVIDOR BACKEND INICIADO
echo  URL: http://127.0.0.1:8000
echo ========================================
echo.
echo 📋 NOTAS:
echo - La primera vez descargara el modelo Whisper Small (~460MB)
echo - Mantén esta ventana abierta mientras uses la aplicación
echo - Presiona Ctrl+C para detener el servidor
echo.

python main.py

pause