"""
Módulo de carregamento e cache das bases de dados públicas municipais.
Aplica cache em memória (@st.cache_data) para resposta instantânea na interface.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

# Fallback gracioso para st.cache_data quando executado fora do runtime do Streamlit (ex: pytest)
try:
    import streamlit as st
    cache_decorator = st.cache_data
except ImportError:
    def cache_decorator(func):
        return func

DATA_DIR = Path(__file__).parent.parent / "data"


@cache_decorator
def carregar_indicadores() -> pd.DataFrame:
    """
    Carrega os indicadores socioeconômicos dos 96 distritos de São Paulo.
    Retorna um DataFrame Pandas estruturado e tipado.
    """
    caminho = DATA_DIR / "indicadores_socioeconomicos.json"
    if not caminho.exists():
        raise FileNotFoundError(f"Base de indicadores não encontrada em: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    df = pd.DataFrame(dados)
    # Conversões e tipos seguros
    df["populacao"] = df["populacao"].astype(int)
    df["renda_media_formal"] = df["renda_media_formal"].astype(float)
    df["tempo_deslocamento_min"] = df["tempo_deslocamento_min"].astype(float)
    df["empregos_por_100hab"] = df["empregos_por_100hab"].astype(float)
    df["equipamentos_adesampa_ativos"] = df["equipamentos_adesampa_ativos"].astype(int)
    df["indice_deserto_fomento"] = df["indice_deserto_fomento"].astype(float)

    return df


@cache_decorator
def carregar_equipamentos() -> List[Dict[str, Any]]:
    """
    Carrega o catálogo georreferenciado das unidades ativas da ADE SAMPA
    (Rede Teia, FabLabs Livres SP e Postos de Atendimento).
    """
    caminho = DATA_DIR / "equipamentos_adesampa.json"
    if not caminho.exists():
        raise FileNotFoundError(f"Catálogo de equipamentos não encontrado em: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


@cache_decorator
def carregar_geojson_distritos() -> Dict[str, Any]:
    """
    Carrega a malha cartográfica vetorial dos 96 distritos de São Paulo.
    """
    caminho = DATA_DIR / "distritos_sp.geojson"
    if not caminho.exists():
        raise FileNotFoundError(f"Malha GeoJSON não encontrada em: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)
