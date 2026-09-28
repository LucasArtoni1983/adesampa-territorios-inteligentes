"""
Módulo de análise e métricas analíticas territoriais.
Calcula indicadores agregados, rankings e filtros espaciais por zona e subprefeitura.
"""

from typing import Any, Dict, List, Optional
import pandas as pd


def obter_metricas_gerais(df: pd.DataFrame, equipamentos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Retorna estatísticas consolidadas do município de São Paulo.
    """
    populacao_total = int(df["populacao"].sum())
    renda_media_cidade = float(df["renda_media_formal"].mean())
    tempo_medio_deslocamento = float(df["tempo_deslocamento_min"].mean())
    total_equipamentos = len(equipamentos)
    
    # Contagem de desertos críticos (IDF >= 7.5)
    desertos_criticos = int((df["indice_deserto_fomento"] >= 7.5).sum())
    populacao_em_desertos = int(df[df["indice_deserto_fomento"] >= 7.5]["populacao"].sum())

    # Total por tipo de equipamento
    teias = sum(1 for e in equipamentos if e.get("tipo") == "Rede Teia")
    fablabs = sum(1 for e in equipamentos if e.get("tipo") == "FabLab Livre")
    postos = sum(1 for e in equipamentos if e.get("tipo") == "Posto de Atendimento")

    return {
        "populacao_total": populacao_total,
        "renda_media_cidade": round(renda_media_cidade, 2),
        "tempo_medio_deslocamento": round(tempo_medio_deslocamento, 1),
        "total_equipamentos": total_equipamentos,
        "total_teias": teias,
        "total_fablabs": fablabs,
        "total_postos": postos,
        "desertos_criticos_qtd": desertos_criticos,
        "populacao_em_desertos": populacao_em_desertos,
    }


def filtrar_dados(
    df: pd.DataFrame,
    zonas: Optional[List[str]] = None,
    subprefeitura: Optional[str] = None,
    apenas_desertos: bool = False,
    busca_nome: Optional[str] = None
) -> pd.DataFrame:
    """
    Aplica filtros combinados sobre o conjunto de distritos.
    """
    filtrado = df.copy()

    if zonas and "Todas" not in zonas:
        filtrado = filtrado[filtrado["zona"].isin(zonas)]

    if subprefeitura and subprefeitura != "Todas":
        filtrado = filtrado[filtrado["subprefeitura"] == subprefeitura]

    if apenas_desertos:
        filtrado = filtrado[filtrado["indice_deserto_fomento"] >= 5.5]

    if busca_nome:
        termo = busca_nome.strip().lower()
        filtrado = filtrado[filtrado["distrito"].str.lower().str.contains(termo, na=False)]

    return filtrado


def obter_ranking_vulnerabilidade(df: pd.DataFrame, top_n: int = 10, ascendente: bool = False) -> pd.DataFrame:
    """
    Retorna os distritos ordenados por prioridade/deserto de fomento produtivo.
    ascendente=False: Maiores desertos (mais vulneráveis) primeiro.
    ascendente=True: Polos mais consolidados (menos vulneráveis) primeiro.
    """
    colunas = [
        "distrito", "subprefeitura", "zona", "populacao",
        "renda_media_formal", "tempo_deslocamento_min",
        "empregos_por_100hab", "equipamentos_adesampa_ativos",
        "indice_deserto_fomento", "classificacao_vulnerabilidade"
    ]
    return df.sort_values(by="indice_deserto_fomento", ascending=ascendente)[colunas].head(top_n)


def buscar_equipamentos_por_distrito(
    equipamentos: List[Dict[str, Any]],
    nome_distrito: str
) -> List[Dict[str, Any]]:
    """
    Retorna os equipamentos localizados exatamente no distrito selecionado.
    """
    termo = nome_distrito.strip().lower()
    return [e for e in equipamentos if e.get("distrito", "").strip().lower() == termo]


def exportar_figura_png(
    fig: Any,
    largura: int = 1200,
    altura: int = 650,
    escala: float = 2.0
) -> bytes:
    """
    Exporta uma figura Plotly para bytes PNG em alta definição (300 DPI equivalente).
    Executado de forma segura sob demanda (lazy evaluation).
    """
    try:
        return fig.to_image(format="png", width=largura, height=altura, scale=escala)
    except Exception:
        # Fallback para renderização básica sem escala caso haja restrição
        return fig.to_image(format="png")


def obter_config_plotly_export(nome_arquivo: str = "grafico_adesampa") -> Dict[str, Any]:
    """
    Retorna o dicionário de configuração da barra interativa Plotly (ModeBar)
    com botão nativo de exportação PNG em alta resolução.
    """
    nome_sanitizado = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in nome_arquivo)
    return {
        "displayModeBar": True,
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": nome_sanitizado,
            "height": 700,
            "width": 1200,
            "scale": 2.5
        }
    }
