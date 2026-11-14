@echo off
setlocal
cd /d "%~dp0"
title GolStats

rem --- 1) Buscar Python ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto nopython

rem --- 2) Entorno virtual (solo la primera vez) ---
if exist "venv\Scripts\python.exe" goto havevenv
echo Preparando GolStats por primera vez (puede tardar un minuto)...
%PY% -m venv venv
if errorlevel 1 goto fail
:havevenv

rem --- 3) Dependencias (rapido si ya estan instaladas) ---
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto fail

rem --- 4) API key de football-data.org ---
if exist ".env" goto envok
echo.
echo Falta la API key de football-data.org.
set /p KEY=Pega tu API key y presiona Enter: 
if "%KEY%"=="" goto nokey
>".env" echo FOOTBALL_API_KEY=%KEY%
:envok

rem --- 5) Iniciar ---
"venv\Scripts\python.exe" run.py
if errorlevel 1 goto fail
goto end

:nopython
echo.
echo No se encontro Python en esta PC.
echo Instalalo desde https://www.python.org/downloads/ y marca "Add Python to PATH".
start https://www.python.org/downloads/
pause
exit /b 1

:nokey
echo.
echo No se ingreso ninguna API key. Volve a abrir iniciar.bat cuando la tengas.
pause
exit /b 1

:fail
echo.
echo Algo salio mal. Copia el mensaje de arriba y pasaselo a quien te ayuda con el proyecto.
pause
exit /b 1

:end
endlocal
