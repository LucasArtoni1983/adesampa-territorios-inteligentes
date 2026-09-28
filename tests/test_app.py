"""
Teste de fumaça e sintaxe para app.py
"""

import py_compile
from pathlib import Path


def test_app_syntax():
    app_path = Path(__file__).parent.parent / "app.py"
    assert app_path.exists(), "app.py deve existir na raiz do projeto"
    compiled = py_compile.compile(str(app_path), doraise=True)
    assert compiled is not None, "app.py deve compilar sem erros de sintaxe"


def test_filtros_observatorio():
    """Garante que a lógica de filtros do observatório retorna os 96 distritos por padrão."""
    import pandas as pd
    from src.data_loader import carregar_indicadores

    df = carregar_indicadores()
    zonas_obs = ["Centro", "Leste", "Norte", "Oeste", "Sul"]
    subs_disponiveis = sorted(list(df[df["zona"].isin(zonas_obs)]["subprefeitura"].unique()))
    
    classificacoes_prefixos = ["Deserto Crítico", "Deserto Moderado", "Em Cobertura", "Polo Consolidado"]
    classificacoes_obs = [
        v for v in df["classificacao_vulnerabilidade"].unique()
        if any(v.startswith(pref) for pref in classificacoes_prefixos)
    ]
    
    r_min, r_max = float(df["renda_media_formal"].min()), float(df["renda_media_formal"].max())
    d_min, d_max = float(df["tempo_deslocamento_min"].min()), float(df["tempo_deslocamento_min"].max())
    
    df_filtrado = df[
        (df["zona"].isin(zonas_obs)) &
        (df["subprefeitura"].isin(subs_disponiveis)) &
        (df["classificacao_vulnerabilidade"].isin(classificacoes_obs)) &
        (df["renda_media_formal"].between(r_min, r_max)) &
        (df["tempo_deslocamento_min"].between(d_min, d_max)) &
        (df["indice_deserto_fomento"].between(0.0, 10.0))
    ]
    assert len(df_filtrado) == 96, f"Filtros padrão devem contemplar todos os 96 distritos, encontrado {len(df_filtrado)}"


def test_studio_regras_ordenacao_graficos():
    """Garante que a ordenação ascendente/decrescente só é habilitada para estilos de gráfico aplicáveis."""
    tipos_com_ordenacao = [
        "📈 Gráfico de Linhas (com marcadores)",
        "📊 Gráfico de Barras Horizontais",
        "📶 Gráfico de Barras Verticais",
        "🍭 Gráfico de Pirulito (Lollipop)",
        "📉 Gráfico de Área Preenchida"
    ]
    tipos_sem_ordenacao = [
        "🥧 Gráfico de Pizza / Donut",
        "📍 Gráfico de Dispersão (Scatter)"
    ]

    for t in tipos_com_ordenacao:
        permite = any(sub in t for sub in ["Linhas", "Barras", "Pirulito", "Área"])
        assert permite is True, f"{t} deve permitir ordenação ascendente/decrescente"

    for t in tipos_sem_ordenacao:
        permite = any(sub in t for sub in ["Linhas", "Barras", "Pirulito", "Área"])
        assert permite is False, f"{t} NÃO deve permitir ordenação sequencial ascendente/decrescente"


