#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  Iniciando ADE SAMPA Territórios Inteligentes (Web)"
echo "  Edital 005/2026 - Assistente II - Dados e IA"
echo "========================================================"

if [ ! -d "venv" ]; then
    echo "[1/3] Criando ambiente virtual Python..."
    python3 -m venv venv
    echo "[2/3] Instalando dependências..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "[3/3] Iniciando aplicação Streamlit..."
streamlit run app.py
