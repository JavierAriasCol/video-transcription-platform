@echo off
title Video Transcription Platform
color 0A

echo.
echo  ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ████████╗████████╗
echo  ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ╚══██╔══╝╚══██╔══╝
echo  ██║   ██║██║██║  ██║█████╗  ██║   ██║       ██║      ██║   
echo  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║       ██║      ██║   
echo   ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝       ██║      ██║   
echo    ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝        ╚═╝      ╚═╝   
echo.
echo  ████████╗██████╗  █████╗ ███╗   ██╗███████╗ ██████╗██████╗ 
echo  ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗
echo     ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ██████╔╝
echo     ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██╗
echo     ██║   ██║  ██║██║  ██║██║ ╚████║███████║╚██████╗██║  ██║
echo     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝
echo.
echo ========================================================================
echo                    PLATAFORMA DE TRANSCRIPCION DE VIDEOS
echo                          Powered by OpenAI Whisper
echo ========================================================================
echo.

set "SCRIPT_DIR=%~dp0"

echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no esta instalado
    echo    Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [2/3] Iniciando Backend (Servidor API)...
echo     - Ubicacion: %SCRIPT_DIR%backend
echo     - Puerto: 8000
echo     - URL: http://127.0.0.1:8000

start "Backend - Video Transcription API" cmd /k "cd /d "%SCRIPT_DIR%backend" && (if not exist venv python -m venv venv) && call venv\Scripts\activate.bat && (pip show fastapi >nul 2>&1 || pip install -r requirements.txt) && echo. && echo ✅ Backend iniciado en http://127.0.0.1:8000 && echo. && python main.py"

echo ⏳ Esperando que el backend se inicie...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Iniciando Frontend (Interfaz Web)...
echo     - Ubicacion: %SCRIPT_DIR%frontend  
echo     - Puerto: 3000
echo     - URL: http://localhost:3000

start "Frontend - Video Transcription UI" cmd /k "cd /d "%SCRIPT_DIR%frontend" && echo. && echo ✅ Frontend iniciado en http://localhost:3000 && echo. && start http://localhost:3000 && python -m http.server 3000"

echo.
echo ========================================================================
echo                              ✅ APLICACION INICIADA
echo ========================================================================
echo.
echo 🌐 Abre tu navegador en: http://localhost:3000
echo.
echo 📋 INSTRUCCIONES DE USO:
echo    1. Selecciona el idioma del video (Español o Inglés)
echo    2. Arrastra o selecciona tu video (máximo 2 minutos)
echo    3. Haz clic en "Transcribir Video"
echo    4. Espera el procesamiento (30-60 segundos)
echo    5. Descarga tu archivo VTT
echo.
echo ⚠️  NOTAS IMPORTANTES:
echo    - La primera vez descargará el modelo Whisper Small (~460MB)
echo    - Mantén ambas ventanas de terminal abiertas
echo    - Para detener: Cierra las ventanas o presiona Ctrl+C
echo.
echo ========================================================================

pause