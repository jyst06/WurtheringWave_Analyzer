@echo off
net session >nul 2>&1
if not %errorLevel% == 0 (
    echo Set UAC = CreateObject("Shell.Application") > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "updater.exe", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
) else (
    start "" "updater.exe"
)
