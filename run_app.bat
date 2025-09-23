@echo off
echo Starting Menu Enrichment Streamlit App...
echo.
echo Navigate to: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

cd "c:\Users\mzaye\OneDrive\Documents\Projects\Uber_GenAI\menu-enrichment"
"C:/Users/mzaye/OneDrive/Documents/Projects/Uber_GenAI/.venv/Scripts/streamlit.exe" run streamlit_app/app.py

pause