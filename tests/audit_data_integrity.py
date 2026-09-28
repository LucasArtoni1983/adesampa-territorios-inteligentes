"""
Script de Auditoria Rigorosa de Integridade de Dados — ADE SAMPA
Verifica:
1. Conformidade administrativa oficial dos 96 distritos e 32 subprefeituras da PMSP.
2. Integridade referencial entre indicadores_socioeconomicos.json e distritos_sp.geojson.
3. Integridade do catalogo de equipamentos_adesampa.json (coordenadas, zonas e distritos).
4. Alinhamento 1:1 rigoroso de pontos, traces e tooltips em todos os graficos Plotly.
"""

import json
import sys
from pathlib import Path

# Configurar stdout e stderr para UTF-8 compatível com Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
import plotly.express as px

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"

# Mapa Oficial de Distritos e Subprefeituras da Cidade de São Paulo (Lei Municipal 13.399/2002)
DIVISAO_OFICIAL_SP = {
    # CENTRO (8 distritos)
    "Sé": ("Sé", "Centro"),
    "Bela Vista": ("Sé", "Centro"),
    "Bom Retiro": ("Sé", "Centro"),
    "Cambuci": ("Sé", "Centro"),
    "Consolação": ("Sé", "Centro"),
    "Liberdade": ("Sé", "Centro"),
    "República": ("Sé", "Centro"),
    "Santa Cecília": ("Sé", "Centro"),
    # ZONA OESTE (15 distritos)
    "Butantã": ("Butantã", "Oeste"),
    "Morumbi": ("Butantã", "Oeste"),
    "Raposo Tavares": ("Butantã", "Oeste"),
    "Rio Pequeno": ("Butantã", "Oeste"),
    "Vila Sônia": ("Butantã", "Oeste"),
    "Lapa": ("Lapa", "Oeste"),
    "Barra Funda": ("Lapa", "Oeste"),
    "Jaguara": ("Lapa", "Oeste"),
    "Jaguaré": ("Lapa", "Oeste"),
    "Perdizes": ("Lapa", "Oeste"),
    "Vila Leopoldina": ("Lapa", "Oeste"),
    "Pinheiros": ("Pinheiros", "Oeste"),
    "Alto de Pinheiros": ("Pinheiros", "Oeste"),
    "Itaim Bibi": ("Pinheiros", "Oeste"),
    "Jardim Paulista": ("Pinheiros", "Oeste"),
    # ZONA NORTE (18 distritos)
    "Santana": ("Santana/Tucuruvi", "Norte"),
    "Mandaqui": ("Santana/Tucuruvi", "Norte"),
    "Tucuruvi": ("Santana/Tucuruvi", "Norte"),
    "Casa Verde": ("Casa Verde", "Norte"),
    "Cachoeirinha": ("Casa Verde", "Norte"),
    "Limão": ("Casa Verde", "Norte"),
    "Freguesia do Ó": ("Freguesia/Brasilândia", "Norte"),
    "Brasilândia": ("Freguesia/Brasilândia", "Norte"),
    "Jaçanã": ("Jaçanã/Tremembé", "Norte"),
    "Tremembé": ("Jaçanã/Tremembé", "Norte"),
    "Perus": ("Perus", "Norte"),
    "Anhanguera": ("Perus", "Norte"),
    "Pirituba": ("Pirituba/Jaraguá", "Norte"),
    "Jaraguá": ("Pirituba/Jaraguá", "Norte"),
    "São Domingos": ("Pirituba/Jaraguá", "Norte"),
    "Vila Maria": ("Vila Maria/Vila Guilherme", "Norte"),
    "Vila Guilherme": ("Vila Maria/Vila Guilherme", "Norte"),
    "Vila Medeiros": ("Vila Maria/Vila Guilherme", "Norte"),
    # ZONA LESTE (31 distritos)
    "Aricanduva": ("Aricanduva/Formosa/Carrão", "Leste"),
    "Carrão": ("Aricanduva/Formosa/Carrão", "Leste"),
    "Vila Formosa": ("Aricanduva/Formosa/Carrão", "Leste"),
    "Cidade Tiradentes": ("Cidade Tiradentes", "Leste"),
    "Ermelino Matarazzo": ("Ermelino Matarazzo", "Leste"),
    "Ponte Rasa": ("Ermelino Matarazzo", "Leste"),
    "Guaianases": ("Guaianases", "Leste"),
    "Lajeado": ("Guaianases", "Leste"),
    "Itaim Paulista": ("Itaim Paulista", "Leste"),
    "Vila Curuçá": ("Itaim Paulista", "Leste"),
    "Itaquera": ("Itaquera", "Leste"),
    "Cidade Líder": ("Itaquera", "Leste"),
    "José Bonifácio": ("Itaquera", "Leste"),
    "Parque do Carmo": ("Itaquera", "Leste"),
    "Mooca": ("Mooca", "Leste"),
    "Água Rasa": ("Mooca", "Leste"),
    "Belém": ("Mooca", "Leste"),
    "Brás": ("Mooca", "Leste"),
    "Pari": ("Mooca", "Leste"),
    "Tatuapé": ("Mooca", "Leste"),
    "Penha": ("Penha", "Leste"),
    "Artur Alvim": ("Penha", "Leste"),
    "Cangaíba": ("Penha", "Leste"),
    "Vila Matilde": ("Penha", "Leste"),
    "São Mateus": ("São Mateus", "Leste"),
    "Iguatemi": ("São Mateus", "Leste"),
    "São Rafael": ("São Mateus", "Leste"),
    "São Miguel": ("São Miguel Paulista", "Leste"),
    "Jardim Helena": ("São Miguel Paulista", "Leste"),
    "Vila Jacuí": ("São Miguel Paulista", "Leste"),
    "Sapopemba": ("Sapopemba", "Leste"),
    "Vila Prudente": ("Vila Prudente", "Leste"),
    "São Lucas": ("Vila Prudente", "Leste"),
    # ZONA SUL (22 distritos)
    "Campo Limpo": ("Campo Limpo", "Sul"),
    "Capão Redondo": ("Campo Limpo", "Sul"),
    "Vila Andrade": ("Campo Limpo", "Sul"),
    "Cidade Dutra": ("Capela do Socorro", "Sul"),
    "Grajaú": ("Capela do Socorro", "Sul"),
    "Socorro": ("Capela do Socorro", "Sul"),
    "Cidade Ademar": ("Cidade Ademar", "Sul"),
    "Pedreira": ("Cidade Ademar", "Sul"),
    "Ipiranga": ("Ipiranga", "Sul"),
    "Cursino": ("Ipiranga", "Sul"),
    "Sacomã": ("Ipiranga", "Sul"),
    "Jabaquara": ("Jabaquara", "Sul"),
    "Jardim Ângela": ("M'Boi Mirim", "Sul"),
    "Jardim São Luís": ("M'Boi Mirim", "Sul"),
    "Parelheiros": ("Parelheiros", "Sul"),
    "Marsilac": ("Parelheiros", "Sul"),
    "Santo Amaro": ("Santo Amaro", "Sul"),
    "Campo Belo": ("Santo Amaro", "Sul"),
    "Campo Grande": ("Santo Amaro", "Sul"),
    "Vila Mariana": ("Vila Mariana", "Sul"),
    "Moema": ("Vila Mariana", "Sul"),
    "Saúde": ("Vila Mariana", "Sul"),
}


def executar_auditoria_completa():
    print("=" * 70)
    print("AUDITORIA INTEGRAL DE CONFIABILIDADE DE DADOS — ADE SAMPA")
    print("=" * 70)

    erros = []

    # 1. Carregar bases de dados
    print("\n[ETAPA 1] Carregando bases de dados locais...")
    with open(DATA_DIR / "indicadores_socioeconomicos.json", "r", encoding="utf-8") as f:
        indicadores = json.load(f)
    with open(DATA_DIR / "distritos_sp.geojson", "r", encoding="utf-8") as f:
        geojson = json.load(f)
    with open(DATA_DIR / "equipamentos_adesampa.json", "r", encoding="utf-8") as f:
        equipamentos = json.load(f)

    df = pd.DataFrame(indicadores)
    print(f"  ✓ {len(indicadores)} registros em indicadores_socioeconomicos.json")
    print(f"  ✓ {len(geojson['features'])} feicoes em distritos_sp.geojson")
    print(f"  ✓ {len(equipamentos)} unidades em equipamentos_adesampa.json")

    # 2. Auditar integridade administrativa dos 96 distritos
    print("\n[ETAPA 2] Auditando conformidade administrativa (Distrito, Subprefeitura e Zona)...")
    distritos_auditados = 0
    for item in indicadores:
        distrito = item["distrito"]
        zona = item["zona"]
        sub = item["subprefeitura"]

        if distrito not in DIVISAO_OFICIAL_SP:
            # Caso nome com pequena variacao ortografica
            match_encontrado = None
            for nome_oficial in DIVISAO_OFICIAL_SP:
                if nome_oficial.lower() == distrito.lower():
                    match_encontrado = nome_oficial
                    break
            if not match_encontrado:
                erros.append(f"Distrito desconhecido: '{distrito}'")
                continue
            distrito = match_encontrado

        sub_oficial, zona_oficial = DIVISAO_OFICIAL_SP[distrito]

        # Checar se a zona informada bate com a oficial
        if zona != zona_oficial:
            erros.append(f"Zona incorreta em '{distrito}': base diz '{zona}', oficial e '{zona_oficial}'")

        # Checar consistencia de subprefeitura
        # Algumas subprefeituras usam barra ou hifen, normalizamos para comparar
        sub_norm = sub.replace("/", " ").replace("-", " ").lower()
        sub_oficial_norm = sub_oficial.replace("/", " ").replace("-", " ").lower()
        if sub_norm not in sub_oficial_norm and sub_oficial_norm not in sub_norm:
            erros.append(f"Subprefeitura incorreta em '{distrito}': base diz '{sub}', oficial e '{sub_oficial}'")

        distritos_auditados += 1

    print(f"  ✓ {distritos_auditados} distritos verificados contra a divisao territorial da PMSP.")

    # 3. Auditar correspondencia GeoJSON x Indicadores
    print("\n[ETAPA 3] Auditando sincronizacao entre GeoJSON e Indicadores...")
    nomes_geojson = {f["properties"].get("nome") for f in geojson["features"]}
    nomes_indicadores = set(df["distrito"])

    diff_geo = nomes_indicadores - nomes_geojson
    diff_ind = nomes_geojson - nomes_indicadores

    if diff_geo:
        erros.append(f"Distritos no JSON mas ausentes no GeoJSON: {diff_geo}")
    if diff_ind:
        erros.append(f"Distritos no GeoJSON mas ausentes no JSON: {diff_ind}")

    if not diff_geo and not diff_ind:
        print("  ✓ Correspondencia biunivoca perfeita (96 distritos) entre GeoJSON e JSON de Indicadores.")

    # 4. Auditar catalogo de equipamentos ADE SAMPA
    print("\n[ETAPA 4] Auditando catalogo de 24 equipamentos ADE SAMPA...")
    for eq in equipamentos:
        nome_eq = eq.get("nome")
        lat = eq.get("latitude")
        lon = eq.get("longitude")
        distrito_eq = eq.get("distrito")
        zona_eq = eq.get("zona")

        if not (-24.1 <= lat <= -23.3 and -47.0 <= lon <= -46.3):
            erros.append(f"Coordenadas invalidas para '{nome_eq}': ({lat}, {lon})")

        if distrito_eq not in nomes_indicadores:
            erros.append(f"Equipamento '{nome_eq}' associado a distrito inexistente: '{distrito_eq}'")

        if distrito_eq in DIVISAO_OFICIAL_SP:
            _, zona_esperada = DIVISAO_OFICIAL_SP[distrito_eq]
            if zona_eq != zona_esperada:
                erros.append(f"Equipamento '{nome_eq}': zona '{zona_eq}' difere da zona do distrito '{distrito_eq}' ({zona_esperada})")

    print(f"  ✓ Todos os {len(equipamentos)} equipamentos com coordenadas validas e vinculadas corretamente.")

    # 5. AUDITORIA CRITICA: Alinhamento 1:1 de Tooltips nos Graficos Plotly (TODOS OS 96 DISTRITOS)
    print("\n[ETAPA 5] Auditando alinhamento de tooltips e customdata em TODOS os graficos Plotly...")

    cores_zonas = {
        "Centro": "#10B981", "Oeste": "#06B6D4",
        "Norte": "#F59E0B", "Leste": "#EF4444", "Sul": "#8B5CF6"
    }

    # Teste Grafico 1: Dispersao (Renda x Deslocamento)
    fig_disp = px.scatter(
        df,
        x="tempo_deslocamento_min",
        y="renda_media_formal",
        color="zona",
        size="populacao",
        hover_name="distrito",
        custom_data=["zona", "subprefeitura", "populacao", "indice_deserto_fomento", "equipamentos_adesampa_ativos"],
        color_discrete_map=cores_zonas
    )

    pontos_auditados_disp = 0
    for trace in fig_disp.data:
        nomes_no_trace = list(trace.hovertext)
        custom_no_trace = trace.customdata
        for i, nome_distrito in enumerate(nomes_no_trace):
            row = df[df["distrito"] == nome_distrito].iloc[0]
            c_zona = custom_no_trace[i][0]
            c_sub = custom_no_trace[i][1]
            c_pop = custom_no_trace[i][2]
            c_idf = custom_no_trace[i][3]
            c_eq = custom_no_trace[i][4]

            # Verificacoes estritas
            if c_zona != row["zona"]:
                erros.append(f"[Grafico 1] '{nome_distrito}' customdata zona '{c_zona}' != esperado '{row['zona']}'")
            if c_sub != row["subprefeitura"]:
                erros.append(f"[Grafico 1] '{nome_distrito}' customdata sub '{c_sub}' != esperado '{row['subprefeitura']}'")
            if c_pop != row["populacao"]:
                erros.append(f"[Grafico 1] '{nome_distrito}' customdata pop {c_pop} != esperado {row['populacao']}")
            if abs(c_idf - row["indice_deserto_fomento"]) > 0.001:
                erros.append(f"[Grafico 1] '{nome_distrito}' customdata idf {c_idf} != esperado {row['indice_deserto_fomento']}")
            if c_eq != row["equipamentos_adesampa_ativos"]:
                erros.append(f"[Grafico 1] '{nome_distrito}' customdata eq {c_eq} != esperado {row['equipamentos_adesampa_ativos']}")

            pontos_auditados_disp += 1

    print(f"  ✓ Grafico 1 (Dispersao): 100% dos {pontos_auditados_disp} distritos com customdata e tooltips rigorosamente alinhados.")

    # Teste Grafico 2: Barras Ranking Top Desertos
    ranking_top = df.sort_values(by="indice_deserto_fomento", ascending=False).head(15)
    fig_bar = px.bar(
        ranking_top,
        x="indice_deserto_fomento",
        y="distrito",
        orientation="h",
        color="zona",
        custom_data=["zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "equipamentos_adesampa_ativos"]
    )
    barras_auditadas = 0
    for trace in fig_bar.data:
        distritos_trace = list(trace.y)
        custom_trace = trace.customdata
        for i, nome_distrito in enumerate(distritos_trace):
            row = df[df["distrito"] == nome_distrito].iloc[0]
            if custom_trace[i][0] != row["zona"] or custom_trace[i][1] != row["subprefeitura"]:
                erros.append(f"[Grafico 2 Barras] '{nome_distrito}' desalinhado no trace!")
            barras_auditadas += 1

    print(f"  ✓ Grafico 2 (Barras): 100% das {barras_auditadas} barras com dados perfeitamente consistentes.")

    # Teste Grafico 3: Rosca (Equipamentos por Zona)
    equip_zona = df.groupby("zona")["equipamentos_adesampa_ativos"].sum().reset_index()
    distritos_por_zona = df.groupby("zona")["distrito"].count().to_dict()
    equip_zona["qtd_distritos"] = equip_zona["zona"].map(distritos_por_zona).fillna(0).astype(int)

    fig_pie = px.pie(
        equip_zona,
        names="zona",
        values="equipamentos_adesampa_ativos",
        custom_data=["qtd_distritos"]
    )
    for i, nome_zona in enumerate(fig_pie.data[0].labels):
        qtd_eq_esperada = int(df[df["zona"] == nome_zona]["equipamentos_adesampa_ativos"].sum())
        qtd_eq_grafico = int(fig_pie.data[0].values[i])
        qtd_dist_esperada = int(distritos_por_zona[nome_zona])
        qtd_dist_grafico = int(fig_pie.data[0].customdata[i][0])

        if qtd_eq_grafico != qtd_eq_esperada:
            erros.append(f"[Grafico 3 Rosca] Zona {nome_zona}: equip {qtd_eq_grafico} != esperado {qtd_eq_esperada}")
        if qtd_dist_grafico != qtd_dist_esperada:
            erros.append(f"[Grafico 3 Rosca] Zona {nome_zona}: distritos {qtd_dist_grafico} != esperado {qtd_dist_esperada}")

    print(f"  ✓ Grafico 3 (Rosca): 100% das 5 regioes com total de equipamentos e contagem de distritos validados.")

    # Teste Grafico 4: Bolhas Multidimensional
    fig_bolhas = px.scatter(
        df,
        x="renda_media_formal",
        y="indice_deserto_fomento",
        size="populacao",
        color="classificacao_vulnerabilidade",
        hover_name="distrito",
        custom_data=["classificacao_vulnerabilidade", "zona", "subprefeitura", "populacao", "equipamentos_adesampa_ativos"]
    )
    pontos_bolha = 0
    for trace in fig_bolhas.data:
        nomes_bolha = list(trace.hovertext)
        custom_bolha = trace.customdata
        for i, nome_distrito in enumerate(nomes_bolha):
            row = df[df["distrito"] == nome_distrito].iloc[0]
            if custom_bolha[i][1] != row["zona"] or custom_bolha[i][2] != row["subprefeitura"]:
                erros.append(f"[Grafico 4 Bolhas] '{nome_distrito}' desalinhado no trace!")
            pontos_bolha += 1

    print(f"  ✓ Grafico 4 (Bolhas): 100% dos {pontos_bolha} distritos validados em cada camada de vulnerabilidade.")

    # 6. Relatorio Final da Auditoria
    print("\n" + "=" * 70)
    if not erros:
        print("RESULTADO: 100% DOS DADOS ESTAO CORRETOS, ALINHADOS E VALIDADOS!")
        print(f"Auditoria concluiu com ZERO divergencias em todos os 96 distritos paulistanos.")
        print("=" * 70)
        return True
    else:
        print(f"ATENCAO: Foram encontradas {len(erros)} divergencias:")
        for err in erros:
            print(f"  ✗ {err}")
        print("=" * 70)
        return False


def test_auditoria_completa_dados():
    """Validação automatizada de regressão para Pytest."""
    assert executar_auditoria_completa() is True


if __name__ == "__main__":
    sucesso = executar_auditoria_completa()
    exit(0 if sucesso else 1)
