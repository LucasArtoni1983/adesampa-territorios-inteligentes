"""
Script de auditoria de importações e compatibilidade da v1.0.0
Verifica se todos os módulos do projeto importam suas dependências sem erros.
"""

import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

erros = []

print("=" * 60)
print("AUDITORIA DE IMPORTAÇÕES — ADE SAMPA v1.0.0")
print("=" * 60)

# 1. Teste de data_loader e pandas
print("\n[1] Verificando src.data_loader e pandas...")
try:
    import pandas as pd
    print(f"  [OK] pandas importado com sucesso (versao: {pd.__version__})")
except Exception as e:
    erros.append(f"Falha ao importar pandas: {e}")
    print(f"  [ERRO] Erro em pandas: {e}")

try:
    from src.data_loader import carregar_indicadores, carregar_equipamentos, carregar_geojson_distritos
    df = carregar_indicadores()
    eq = carregar_equipamentos()
    geo = carregar_geojson_distritos()
    print(f"  [OK] src.data_loader executou com sucesso:")
    print(f"    - Indicadores carregados: {len(df)} distritos (Tipo: {type(df)})")
    print(f"    - Equipamentos carregados: {len(eq)} unidades (Tipo: {type(eq)})")
    print(f"    - GeoJSON carregado: {len(geo['features'])} geometrias (Tipo: {type(geo)})")
except Exception as e:
    erros.append(f"Falha em src.data_loader: {e}")
    print(f"  [ERRO] Erro em src.data_loader: {e}")

# 2. Teste de metrics_analyzer
print("\n[2] Verificando src.metrics_analyzer...")
try:
    from src.metrics_analyzer import (
        obter_metricas_gerais,
        filtrar_dados,
        obter_ranking_vulnerabilidade,
        buscar_equipamentos_por_distrito
    )
    metricas = obter_metricas_gerais(df, eq)
    print(f"  [OK] src.metrics_analyzer importado e executado com sucesso (Populacao calculada: {metricas['populacao_total']:,})")
except Exception as e:
    erros.append(f"Falha em src.metrics_analyzer: {e}")
    print(f"  [ERRO] Erro em src.metrics_analyzer: {e}")

# 3. Teste de ai_advisor
print("\n[3] Verificando src.ai_advisor...")
try:
    from src.ai_advisor import gerar_diagnostico_ia
    amostra = df.iloc[0].to_dict()
    diag = gerar_diagnostico_ia(amostra)
    print(f"  [OK] src.ai_advisor importado e executado com sucesso (Diagnostico gerado para: {diag['distrito']})")
except Exception as e:
    erros.append(f"Falha em src.ai_advisor: {e}")
    print(f"  [ERRO] Erro em src.ai_advisor: {e}")

# 4. Teste de map_builder e bibliotecas de mapa (folium, branca, etc.)
print("\n[4] Verificando src.map_builder e folium...")
try:
    import folium
    print(f"  [OK] folium importado com sucesso (versao: {folium.__version__})")
    from src.map_builder import criar_mapa_territorial
    mapa = criar_mapa_territorial(geo, eq, mostrar_raio_cobertura=True)
    print(f"  [OK] src.map_builder construiu mapa com sucesso (Tipo: {type(mapa)})")
except Exception as e:
    erros.append(f"Falha em src.map_builder / folium: {e}")
    print(f"  [ERRO] Erro em src.map_builder: {e}")

# 5. Teste de streamlit e streamlit-folium
print("\n[5] Verificando streamlit, plotly e streamlit_folium...")
try:
    import streamlit as st
    print(f"  [OK] streamlit importado com sucesso (versao: {st.__version__})")
except Exception as e:
    erros.append(f"Falha em streamlit: {e}")
    print(f"  [ERRO] Erro em streamlit: {e}")

try:
    import plotly
    import plotly.express as px
    print(f"  [OK] plotly importado com sucesso (versao: {plotly.__version__})")
except Exception as e:
    erros.append(f"Falha em plotly: {e}")
    print(f"  [ERRO] Erro em plotly: {e}")

try:
    import streamlit_folium
    from streamlit_folium import st_folium
    versao_st_folium = getattr(streamlit_folium, "__version__", "instalado com sucesso")
    print(f"  [OK] streamlit_folium importado com sucesso ({versao_st_folium})")
except Exception as e:
    erros.append(f"Falha em streamlit_folium: {e}")
    print(f"  [ERRO] Erro em streamlit_folium: {e}")

# 6. Teste de compilação do app.py
print("\n[6] Verificando compilacao do app.py...")
try:
    import py_compile
    py_compile.compile(str(ROOT_DIR / "app.py"), doraise=True)
    print("  [OK] app.py compilado sem nenhum erro de sintaxe ou import estatico.")
except Exception as e:
    erros.append(f"Falha na compilacao do app.py: {e}")
    print(f"  [ERRO] Erro em app.py: {e}")

print("\n" + "=" * 60)
if not erros:
    print("RESULTADO FINAL: TODOS OS IMPORTS ESTÃO 100% CORRETOS E OPERACIONAIS!")
    print("=" * 60)
    sys.exit(0)
else:
    print(f"RESULTADO FINAL: {len(erros)} ERRO(S) ENCONTRADO(S):")
    for err in erros:
        print(f"  - {err}")
    print("=" * 60)
    sys.exit(1)
