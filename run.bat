@echo off
echo ========================================================
echo   Iniciando ADE SAMPA Territorios Inteligentes (Web)
echo   Edital 005/2026 - Assistente II - Dados e IA
echo ========================================================

REM Verifica se o ambiente virtual existe, se nao existir, cria e instala dependencias
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Criando ambiente virtual Python...
    python -m venv venv
    echo [2/3] Instalando dependencias do requirements.txt...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo [3/3] Iniciando aplicacao Streamlit em http://localhost:8501...
streamlit run app.py
pause
