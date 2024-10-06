@echo off
:: Check if a port is provided as an argument
if "%1"=="" (
  set port=8502  REM Default port
) else (
  set port=%1
)
:: Execute the streamlit command with the specified or default port
echo Streamlit starting on port %port%...
streamlit run --server.port %port% app.py
pause
