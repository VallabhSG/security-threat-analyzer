@echo off
echo Stopping any existing Ollama processes...
taskkill /F /IM ollama.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Ollama in CPU-only mode...
set OLLAMA_NUM_GPU=0
start "Ollama Server" ollama serve

timeout /t 3 /nobreak >nul

echo.
echo Ollama server started in CPU mode
echo Ready to use with Streamlit app
echo.
pause
