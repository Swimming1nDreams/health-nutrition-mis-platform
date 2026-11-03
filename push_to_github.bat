@echo off
title Push Health MIS Project to GitHub
cd /d "%~dp0"
set "GH_PATH=C:\Program Files\GitHub CLI\gh.exe"

"%GH_PATH%" auth status
if %errorlevel% neq 0 (
    echo [!] Logging in to GitHub...
    "%GH_PATH%" auth login -p https -w -h github.com
)

echo [*] Creating and pushing repository to GitHub...
"%GH_PATH%" repo create health-nutrition-mis-platform --public --source=. --remote=origin --push --description "Humanitarian Health & Nutrition MIS Platform (DHIS2 Validation Rules & JSON API, WHO 2006 Growth Z-scores, SMART DPS Plausibility, Tdh MCCT Maternal Cash, Buffer Stock MoS)"
pause
