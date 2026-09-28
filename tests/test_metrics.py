"""
Testes automatizados para métricas analíticas e motor de IA.
"""

from src.data_loader import carregar_indicadores, carregar_equipamentos
from src.metrics_analyzer import (
    obter_metricas_gerais,
    filtrar_dados,
    obter_ranking_vulnerabilidade,
    buscar_equipamentos_por_distrito,
    exportar_figura_png,
    obter_config_plotly_export
)
from src.ai_advisor import gerar_diagnostico_ia


def test_obter_metricas_gerais():
    df = carregar_indicadores()
    eqs = carregar_equipamentos()
    metricas = obter_metricas_gerais(df, eqs)

    assert metricas["populacao_total"] > 10_000_000, "População de SP deve ser superior a 10 milhões"
    assert metricas["renda_media_cidade"] > 2000.0
    assert metricas["total_equipamentos"] == len(eqs)
    assert metricas["desertos_criticos_qtd"] > 0


def test_filtrar_dados():
    df = carregar_indicadores()
    
    # Filtro por Zona
    df_leste = filtrar_dados(df, zonas=["Leste"])
    assert len(df_leste) > 0
    assert (df_leste["zona"] == "Leste").all()

    # Busca por nome
    df_busca = filtrar_dados(df, busca_nome="Brasilândia")
    assert len(df_busca) == 1
    assert df_busca.iloc[0]["distrito"] == "Brasilândia"


def test_ranking_vulnerabilidade():
    df = carregar_indicadores()
    top5 = obter_ranking_vulnerabilidade(df, top_n=5, ascendente=False)
    assert len(top5) == 5
    # O primeiro deve ter score de deserto maior ou igual ao segundo
    assert top5.iloc[0]["indice_deserto_fomento"] >= top5.iloc[1]["indice_deserto_fomento"]


def test_gerar_diagnostico_ia():
    df = carregar_indicadores()
    dados_brasilandia = df[df["distrito"] == "Brasilândia"].iloc[0].to_dict()
    
    resultado = gerar_diagnostico_ia(dados_brasilandia)
    assert resultado["distrito"] == "Brasilândia"
    assert len(resultado["gargalos"]) > 0
    assert len(resultado["recomendacoes"]) > 0
    assert "relatorio_markdown" in resultado
    assert "Brasilândia" in resultado["relatorio_markdown"]


def test_ordenacao_tempo_deslocamento_asc_desc():
    """Valida a lógica do Studio de Mobilidade: ordenação ascendente e decrescente."""
    df = carregar_indicadores()

    # Ordenação decrescente: o primeiro deve ter tempo maior ou igual ao último
    df_desc = df.sort_values(by="tempo_deslocamento_min", ascending=False)
    assert df_desc.iloc[0]["tempo_deslocamento_min"] >= df_desc.iloc[-1]["tempo_deslocamento_min"]
    assert df_desc.iloc[0]["tempo_deslocamento_min"] >= 65.0, "Distrito com maior tempo em SP deve superar 65 min"

    # Ordenação ascendente: o primeiro deve ter tempo menor ou igual ao último
    df_asc = df.sort_values(by="tempo_deslocamento_min", ascending=True)
    assert df_asc.iloc[0]["tempo_deslocamento_min"] <= df_asc.iloc[-1]["tempo_deslocamento_min"]
    assert df_asc.iloc[0]["tempo_deslocamento_min"] <= 30.0, "Distrito com menor tempo em SP deve ser <= 30 min"

    # Fatiamento Top N
    top10_desc = df_desc.head(10)
    assert len(top10_desc) == 10
    assert list(top10_desc["tempo_deslocamento_min"]) == sorted(list(top10_desc["tempo_deslocamento_min"]), reverse=True)


def test_exportar_figura_png():
    """Valida a exportação sob demanda de figura Plotly em formato PNG."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(x=[1, 2], y=[3, 4]))
    dados_png = exportar_figura_png(fig)
    
    assert isinstance(dados_png, bytes)
    assert len(dados_png) > 1000
    # Valida assinatura do cabeçalho binário PNG (magic number)
    assert dados_png.startswith(b"\x89PNG\r\n\x1a\n")


def test_obter_config_plotly_export():
    """Valida que a configuração do ModeBar inclui parâmetros de imagem de alta definição."""
    cfg = obter_config_plotly_export("grafico_teste_123")
    assert cfg["displayModeBar"] is True
    assert cfg["displaylogo"] is False
    assert "toImageButtonOptions" in cfg
    assert cfg["toImageButtonOptions"]["format"] == "png"
    assert cfg["toImageButtonOptions"]["scale"] >= 2.0
    assert "grafico_teste_123" in cfg["toImageButtonOptions"]["filename"]

