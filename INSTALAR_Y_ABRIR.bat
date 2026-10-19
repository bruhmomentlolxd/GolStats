@echo off
setlocal
cd /d "%~dp0"
title GolStats - Instalacion y apertura

echo ========================================
echo             GOLSTATS
echo    Instalador y acceso para Windows
echo ========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo ERROR: No se encontro Python.
        echo.
        echo Instala Python 3.10 o superior desde https://www.python.org/downloads/windows/
        echo Durante la instalacion, marca "Add Python to PATH".
        echo Luego vuelve a ejecutar este archivo.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creando el entorno de Python...
    %PYTHON% -m venv venv
    if errorlevel 1 goto error
) else (
    echo [1/3] El entorno de Python ya existe.
)

echo.
echo [2/3] Instalando o verificando dependencias...
"venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

if not exist ".env" (
    echo.
    echo No se encontro el archivo privado .env.
    echo Para cargar partidos y estadisticas en vivo necesitas una clave API de football-data.org.
    echo Puedes crear una cuenta y obtenerla en https://www.football-data.org/client/register
    echo.
    set /p "APIKEY=Pegá tu clave API (o presiona Enter para continuar sin ella): "
    if not "%APIKEY%"=="" (
        >".env" echo FOOTBALL_API_KEY=%APIKEY%
        echo Se guardo la clave en .env. No compartas ese archivo ni lo subas a GitHub.
    ) else (
        echo Continuando sin clave API; las consultas en vivo no funcionaran.
    )
    set "APIKEY="
)

echo.
echo [3/3] Iniciando GolStats...
echo Deja esta ventana abierta mientras uses la aplicacion.
echo Para cerrar GolStats, presiona Ctrl+C en esta ventana.
echo.
start "" http://127.0.0.1:5000
"venv\Scripts\python.exe" app.py
goto end

:error
echo.
echo Ocurrio un error al preparar GolStats. Revisa el mensaje anterior.
echo Comprueba que tengas conexion a internet y Python 3.10 o superior.
pause
exit /b 1

:end
endlocal
