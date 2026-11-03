@echo off
title Humanitarian Health & Nutrition MIS Portal
echo ========================================================
echo   Humanitarian Health & Nutrition MIS Operations Portal
echo   (DHIS2 Clinical Data Management & SMART Nutrition)
echo ========================================================
echo.
echo Activating Virtual Environment...
call .venv\Scripts\activate.bat
echo Starting Streamlit Portal on http://localhost:8502 ...
streamlit run app.py --server.port 8502
pause
