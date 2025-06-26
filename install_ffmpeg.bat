@echo off
title Instalacion de FFmpeg
color 0B

echo.
echo ========================================================================
echo                        INSTALACION DE FFMPEG
echo ========================================================================
echo.
echo FFmpeg es necesario para procesar videos. Este script te ayudara a instalarlo.
echo.

echo [1/3] Verificando si FFmpeg ya esta instalado...
ffmpeg -version >nul 2>&1
if not errorlevel 1 (
    echo ✅ FFmpeg ya esta instalado y funcionando
    echo.
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo No es necesario instalar FFmpeg.
    pause
    exit /b 0
)

echo ❌ FFmpeg no esta instalado
echo.

echo [2/3] Opciones de instalacion:
echo.
echo OPCION 1 - Chocolatey (Recomendado)
echo   Si tienes Chocolatey instalado, ejecuta:
echo   choco install ffmpeg
echo.
echo OPCION 2 - Descarga Manual
echo   1. Ve a: https://www.gyan.dev/ffmpeg/builds/
echo   2. Descarga "release builds" ^> "ffmpeg-release-essentials.zip"
echo   3. Extrae el archivo a C:\ffmpeg
echo   4. Agrega C:\ffmpeg\bin al PATH del sistema
echo.
echo OPCION 3 - Winget (Windows 10/11)
echo   winget install ffmpeg
echo.

echo [3/3] Instalacion automatica con Chocolatey...
echo.
echo ¿Quieres intentar instalar FFmpeg con Chocolatey? (s/n)
set /p choice="Respuesta: "

if /i "%choice%"=="s" (
    echo.
    echo Verificando Chocolatey...
    choco --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Chocolatey no esta instalado
        echo.
        echo Para instalar Chocolatey:
        echo 1. Abre PowerShell como Administrador
        echo 2. Ejecuta: Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        echo 3. Reinicia esta ventana y ejecuta este script nuevamente
    ) else (
        echo ✅ Chocolatey encontrado
        echo.
        echo Instalando FFmpeg...
        choco install ffmpeg -y
        
        echo.
        echo Verificando instalacion...
        ffmpeg -version >nul 2>&1
        if not errorlevel 1 (
            echo ✅ FFmpeg instalado correctamente
            ffmpeg -version | findstr "ffmpeg version"
        ) else (
            echo ❌ Error en la instalacion de FFmpeg
            echo Por favor, intenta la instalacion manual
        )
    )
) else (
    echo.
    echo Instalacion cancelada.
    echo Por favor, instala FFmpeg manualmente usando una de las opciones mostradas arriba.
)

echo.
echo ========================================================================
echo                              INSTRUCCIONES
echo ========================================================================
echo.
echo Despues de instalar FFmpeg:
echo 1. Reinicia la terminal/command prompt
echo 2. Ejecuta: ffmpeg -version (para verificar)
echo 3. Ejecuta start_app.bat para iniciar la aplicacion
echo.
echo Si sigues teniendo problemas:
echo - Reinicia tu computadora
echo - Verifica que FFmpeg este en el PATH del sistema
echo - Contacta soporte tecnico
echo.

pause