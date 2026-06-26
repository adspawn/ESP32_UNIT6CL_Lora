@echo off
cd /d "%~dp0"

set "PORT=COM5"
if not "%~1"=="" set "PORT=%~1"

echo ========================================
echo  UNIT-C6L Serial Receiver
echo  Port: %PORT%
echo  Exit: Ctrl+C
echo ========================================
echo.

python receive_serial.py --port %PORT%
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error. Check USB connection and close Meshtastic app.
    echo List ports: python receive_serial.py --list
    pause
)
