@echo off
title Sincronização Automática - GitHub
echo Iniciando script de sincronização automatica com o GitHub...
cd /d "%~dp0"

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe auto_sync.py
) else (
    python auto_sync.py
)
pause
