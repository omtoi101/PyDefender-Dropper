@echo off
echo Building PyDefender executable...

REM --onefile: bundle everything into a single exe
REM --noconsole: no console window will be shown when the exe is run
REM --name: the name of the final executable
REM --paths: tells pyinstaller where to look for modules
pyinstaller --onefile --noconsole --name PyDefender ^
    --paths "AntiDebug" ^
    --paths "AntiVirtulization" ^
    --paths "CriticalProcess" ^
    main.py

if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo.
echo Cleaning up build files...
if exist "build" rmdir /s /q build
if exist "PyDefender.spec" del "PyDefender.spec"

echo.
echo Build complete!
echo The executable can be found in the 'dist' directory.
echo.
pause
