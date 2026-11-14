@echo off
rem Igual que iniciar.bat, pero permite entrar desde el celular si esta en el mismo WiFi.
rem La primera vez Windows pregunta por el Firewall: elegi "Permitir acceso".
set GOLSTATS_LAN=1
call "%~dp0iniciar.bat"
