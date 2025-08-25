@echo off
setlocal enabledelayedexpansion

echo --- PyDefender Compiler ---
echo.

REM --- Step 1: Read URL from config.json ---
echo [1/5] Reading URL from config.json...
set "URL="
REM This is a simple parser. It assumes the "url" key is on its own line.
for /f "tokens=2 delims=:," %%a in ('findstr /i "url" config.json') do (
    set "URL=%%a"
)

REM Clean up quotes and whitespace from the extracted URL
set "URL=!URL:"=!"
for /l %%a in (1,1,32) do set "URL=!URL: =!"
if not defined URL (
    echo [ERROR] Could not read URL from config.json. Please check the file format.
    pause
    exit /b 1
)
echo      URL Found: !URL!
echo.

REM --- Step 2: Create a temporary main script ---
echo [2/5] Creating temporary script for compilation...
set "TEMP_MAIN=main_temp.py"
if exist "%TEMP_MAIN%" del "%TEMP_MAIN%"
copy main.py "%TEMP_MAIN%" > nul
if not exist "%TEMP_MAIN%" (
    echo [ERROR] Could not create temporary file.
    pause
    exit /b 1
)
echo      Temporary script created: %TEMP_MAIN%
echo.

REM --- Step 3: Replace placeholder in the temporary script ---
echo [3/5] Injecting URL into the temporary script...
set "PLACEHOLDER=%%URL_PLACEHOLDER%%"
set "OUT_FILE=%TEMP_MAIN%.tmp"
if exist "%OUT_FILE%" del "%OUT_FILE%"

(
    for /f "usebackq delims=" %%i in ("%TEMP_MAIN%") do (
        set "line=%%i"
        set "line=!line:%PLACEHOLDER%=%URL%!"
        echo !line!
    )
) > "%OUT_FILE%"

move /y "%OUT_FILE%" "%TEMP_MAIN%" > nul
echo      URL injected successfully.
echo.

REM --- Step 4: Run PyInstaller ---
echo [4/5] Running PyInstaller to build the executable...
REM --noconsole is an alternative to --windowed
REM --paths tells pyinstaller where to look for modules.
pyinstaller --onefile --noconsole --name PyDefender ^
    --paths "AntiDebug" ^
    --paths "AntiVirtulization" ^
    --paths "CriticalProcess" ^
    "%TEMP_MAIN%"

if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed with error code %errorlevel%.
    del "%TEMP_MAIN%"
    pause
    exit /b %errorlevel%
)
echo      PyInstaller finished successfully.
echo.

REM --- Step 5: Clean up ---
echo [5/5] Cleaning up temporary files and build artifacts...
if exist "%TEMP_MAIN%" del "%TEMP_MAIN%"
if exist "build" rmdir /s /q build
if exist "PyDefender.spec" del "PyDefender.spec"
echo      Cleanup complete.
echo.

echo --- Build Finished ---
echo The executable can be found in the 'dist' directory.
echo.
pause
