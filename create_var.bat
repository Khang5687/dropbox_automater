@echo off
REM Create required configuration files for Dropbox Automater
REM Run this script before using the automater to set up your session data

echo Creating required configuration files...
echo.

REM Create cookies.txt
if not exist "cookies.txt" (
    echo []> cookies.txt
    echo [92m✓[0m Created cookies.txt (empty - please export your cookies using EditThisCookie extension)
) else (
    echo [93m⊘[0m cookies.txt already exists, skipping...
)

REM Create localstorage.json
if not exist "localstorage.json" (
    echo {}> localstorage.json
    echo [92m✓[0m Created localstorage.json (empty - please export using: copy(JSON.stringify(localStorage)))
) else (
    echo [93m⊘[0m localstorage.json already exists, skipping...
)

REM Create sessionstorage.json
if not exist "sessionstorage.json" (
    echo {}> sessionstorage.json
    echo [92m✓[0m Created sessionstorage.json (empty - please export using: copy(JSON.stringify(sessionStorage)))
) else (
    echo [93m⊘[0m sessionstorage.json already exists, skipping...
)

REM Create useragent.txt
if not exist "useragent.txt" (
    echo Mozilla/5.0 (replace with your actual user agent from navigator.userAgent)> useragent.txt
    echo [92m✓[0m Created useragent.txt (placeholder - please replace with your actual user agent)
) else (
    echo [93m⊘[0m useragent.txt already exists, skipping...
)

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Follow the instructions in HOW_TO_USE.md to export your session data
echo 2. Fill in the created files with your exported data
echo 3. Run: python main.py
echo.

pause
