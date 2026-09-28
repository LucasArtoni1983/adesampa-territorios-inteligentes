"""
Testes de Integridade Referencial e Visualização de Dados — ADE SAMPA
Executa a auditoria completa de 96 distritos, 32 subprefeituras, 24 equipamentos
e alinhamento estrito 1:1 de traces e tooltips dos gráficos.
"""

from tests.audit_data_integrity import executar_auditoria_completa


def test_integridade_distritos_e_graficos():
    """Garante que não há nenhum dado trocado ou desalinhado no sistema."""
    assert executar_auditoria_completa() is True


def test_exportacao_csv_filtrado():
    """Garante que a base filtrada gera CSV válido em utf-8-sig com separador ponto-e-vírgula."""
    import io
    import pandas as pd
    from src.data_loader import carregar_indicadores
    from src.metrics_analyzer import filtrar_dados

    df = carregar_indicadores()
    df_filtrado = filtrar_dados(df, subprefeitura="Perus")
    assert len(df_filtrado) == 2, "Perus possui 2 distritos (Perus e Anhanguera)"

    colunas = [
        "distrito", "subprefeitura", "zona", "populacao",
        "renda_media_formal", "tempo_deslocamento_min",
        "empregos_por_100hab", "equipamentos_adesampa_ativos",
        "indice_deserto_fomento", "classificacao_vulnerabilidade"
    ]
    df_exp = df_filtrado[colunas]
    csv_bytes = df_exp.to_csv(index=False, sep=";").encode("utf-8-sig")

    df_lido = pd.read_csv(io.BytesIO(csv_bytes), sep=";", encoding="utf-8-sig")
    assert len(df_lido) == 2
    assert "Perus" in df_lido["distrito"].values
    assert "Anhanguera" in df_lido["distrito"].values

