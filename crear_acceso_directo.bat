@echo off
rem Crea un icono "GolStats" en el Escritorio para abrir la app con doble clic.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\GolStats.lnk'); $s.TargetPath='%~dp0iniciar.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0static\icons\golstats.ico'; $s.WindowStyle=7; $s.Save()"
if errorlevel 1 goto fail
echo.
echo Listo: ahora tenes el icono GolStats en el Escritorio.
echo (No muevas ni borres esta carpeta, el acceso directo la usa.)
pause
exit /b 0
:fail
echo No se pudo crear el acceso directo.
pause
exit /b 1
