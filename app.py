"""
Aplicação Principal: ADE SAMPA Territórios Inteligentes
Painel Integrado de Diagnóstico Territorial, Cobertura de Equipamentos e Fomento ao Empreendedorismo
Sistema de Inteligência Territorial e Monitoramento de Equipamentos Públicos
"""

import base64
import re
import socket
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium

from src.data_loader import carregar_indicadores, carregar_equipamentos, carregar_geojson_distritos
from src.metrics_analyzer import (
    obter_metricas_gerais,
    filtrar_dados,
    obter_ranking_vulnerabilidade,
    buscar_equipamentos_por_distrito,
    exportar_figura_png,
    obter_config_plotly_export
)
from src.map_builder import criar_mapa_territorial
from src.ai_advisor import gerar_diagnostico_ia

# Diretório raiz e logo oficial local
ROOT_DIR = Path(__file__).parent
LOGO_PATH = ROOT_DIR / "ade-300x300-1-300x300-1-300x300.png"


@st.cache_data(ttl=15)
def verificar_conexao_externa() -> bool:
    """
    Verifica conectividade de rede externa via DNS público com timeout ultrarrápido (0.8s).
    Retorna True se online e False se houver falha de rede/conexão.
    """
    try:
        socket.setdefaulttimeout(0.8)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("8.8.8.8", 53))
        return True
    except (socket.timeout, OSError):
        return False


@st.cache_data
def carregar_logo_base64(caminho_str: str) -> str:
    """Carrega o logotipo local em base64 para renderização instantânea no cabeçalho."""
    p = Path(caminho_str)
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


# 1. Configuração da Página
st.set_page_config(
    page_title="ADE SAMPA Territórios Inteligentes",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS refinada, leve e profissional (Design System Moderno)
st.markdown("""
<style>
    /* Cabeçalho Principal Amigável e Moderno */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #38BDF8 100%);
        padding: 22px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
    }
    .header-content {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .header-logo {
        width: 72px;
        height: 72px;
        border-radius: 14px;
        background: #FFFFFF;
        padding: 6px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15);
        object-fit: contain;
        flex-shrink: 0;
    }
    .header-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 6px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 25px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #F1F5F9 !important;
        font-size: 13.5px;
        margin: 4px 0 0 0;
        opacity: 0.95;
        line-height: 1.4;
    }

    /* BigNumbers / KPI Cards Acessíveis com Texto Alternativo */
    .kpi-card {
        background: #FFFFFF;
        padding: 16px 18px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease-in-out;
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08);
        border-color: #BFDBFE;
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        line-height: 1.2;
    }
    .kpi-icon {
        font-size: 1.15rem;
    }
    .kpi-value {
        font-size: 1.38rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        margin: 4px 0 6px 0;
        word-break: break-word;
    }
    .kpi-alt-text {
        font-size: 0.74rem;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }
    .kpi-alt-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    /* Cards e Elementos Auxiliares */
    .metric-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }
    .metric-card h4 {
        color: #1E3A8A;
        margin: 0 0 10px 0;
        font-size: 16px;
        font-weight: 700;
    }
    .badge-critico {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-moderado {
        background-color: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-atendido {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-consolidado {
        background-color: #F0F9FF;
        color: #0369A1;
        border: 1px solid #BAE6FD;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    /* Estilização suave para abas */
    button[data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
    }

    /* Suavização de contêineres e tabelas */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Centralização elegante do logotipo no canto superior esquerdo (Barra Lateral) */
    [data-testid="stSidebar"] div[data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
    }
    [data-testid="stSidebar"] div[data-testid="stImage"] > img {
        margin: 0 auto !important;
        display: block !important;
        border-radius: 12px;
    }
    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 16px auto;
        text-align: center;
        width: 100%;
    }
    .sidebar-logo-img {
        width: 160px;
        max-width: 100%;
        height: auto;
        border-radius: 14px;
        background: #FFFFFF;
        padding: 8px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
        border: 1px solid #E2E8F0;
        display: block;
        margin: 0 auto;
        transition: transform 0.2s ease-in-out;
    }
    .sidebar-logo-img:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)


# 2. Carregamento dos Dados
df_indicadores = carregar_indicadores()
equipamentos = carregar_equipamentos()
geojson_distritos = carregar_geojson_distritos()
metricas_cidade = obter_metricas_gerais(df_indicadores, equipamentos)


# 3. Barra Lateral (Filtros e Controles)
with st.sidebar:
    # Logotipo oficial da ADE SAMPA centralizado no canto superior esquerdo
    logo_sidebar_b64 = carregar_logo_base64(str(LOGO_PATH))
    if logo_sidebar_b64:
        st.markdown(
            f"""
            <div class="sidebar-logo-container">
                <img src="data:image/png;base64,{logo_sidebar_b64}" 
                     class="sidebar-logo-img" 
                     alt="Logotipo ADE SAMPA" />
            </div>
            """,
            unsafe_allow_html=True
        )
    elif LOGO_PATH.exists():
        col_l, col_m, col_r = st.columns([1, 4, 1])
        with col_m:
            st.image(str(LOGO_PATH), width=160)
    else:
        col_l, col_m, col_r = st.columns([1, 4, 1])
        with col_m:
            st.image("https://adesampa.com.br/wp-content/themes/adesampa/assets/images/logo.png", width=160)

    st.markdown("### 🎛️ Filtros Territoriais")

    # Filtro por Zona
    zonas_disponiveis = ["Todas"] + sorted(list(df_indicadores["zona"].unique()))
    zona_sel = st.selectbox("Zona da Capital:", zonas_disponiveis)

    # Filtro por Subprefeitura
    if zona_sel != "Todas":
        sub_filtradas = sorted(list(df_indicadores[df_indicadores["zona"] == zona_sel]["subprefeitura"].unique()))
    else:
        sub_filtradas = sorted(list(df_indicadores["subprefeitura"].unique()))
    sub_sel = st.selectbox("Subprefeitura:", ["Todas"] + sub_filtradas)

    # Filtro de desertos
    apenas_desertos = st.checkbox("Exibir apenas Desertos de Fomento (IDF ≥ 5.5)", value=False)

    # Busca textual
    busca_nome = st.text_input("🔍 Buscar distrito:", placeholder="Ex: Brasilândia, Grajaú...")

    # Aplicação dos filtros territoriais
    zonas_param = [zona_sel] if zona_sel != "Todas" else None
    df_filtrado = filtrar_dados(
        df_indicadores,
        zonas=zonas_param,
        subprefeitura=sub_sel,
        apenas_desertos=apenas_desertos,
        busca_nome=busca_nome
    )

    # Preparação para exportação CSV da base filtrada (compatível com Excel PT-BR via utf-8-sig e ponto-e-vírgula)
    df_exportar = df_filtrado[[
        "distrito", "subprefeitura", "zona", "populacao",
        "renda_media_formal", "tempo_deslocamento_min",
        "empregos_por_100hab", "equipamentos_adesampa_ativos",
        "indice_deserto_fomento", "classificacao_vulnerabilidade"
    ]].rename(columns={
        "distrito": "Distrito",
        "subprefeitura": "Subprefeitura",
        "zona": "Zona",
        "populacao": "População",
        "renda_media_formal": "Renda Média (R$)",
        "tempo_deslocamento_min": "Tempo Deslocamento (min)",
        "empregos_por_100hab": "Empregos por 100 hab",
        "equipamentos_adesampa_ativos": "Equipamentos Ativos",
        "indice_deserto_fomento": "Índice IDF (0-10)",
        "classificacao_vulnerabilidade": "Classificação"
    })
    csv_filtrado_bytes = df_exportar.to_csv(index=False, sep=";").encode("utf-8-sig")

    if sub_sel != "Todas":
        sufixo_arq = re.sub(r'[^a-zA-Z0-9_-]', '_', sub_sel).lower().strip('_')
        nome_csv_filtrado = f"adesampa_base_subprefeitura_{sufixo_arq}.csv"
    elif zona_sel != "Todas":
        sufixo_arq = re.sub(r'[^a-zA-Z0-9_-]', '_', zona_sel).lower().strip('_')
        nome_csv_filtrado = f"adesampa_base_zona_{sufixo_arq}.csv"
    elif apenas_desertos:
        nome_csv_filtrado = "adesampa_base_desertos_fomento.csv"
    elif busca_nome:
        sufixo_arq = re.sub(r'[^a-zA-Z0-9_-]', '_', busca_nome).lower().strip('_')
        nome_csv_filtrado = f"adesampa_base_busca_{sufixo_arq}.csv"
    else:
        nome_csv_filtrado = "adesampa_base_completa_96_distritos.csv"

    st.markdown("---")
    st.markdown("### 📥 Exportação de Dados")
    st.download_button(
        label=f"📥 Baixar Base Filtrada ({len(df_filtrado)} distritos)",
        data=csv_filtrado_bytes,
        file_name=nome_csv_filtrado,
        mime="text/csv",
        key="dl_btn_sidebar",
        use_container_width=True,
        help="Baixe os dados socioeconômicos dos distritos filtrados em formato CSV (compatível com Excel)."
    )

    # Botão de acesso ao PDF ilustrado do Mapa do Site
    pdf_path_side = ROOT_DIR / "data" / "mapa_do_site_adesampa.pdf"
    if pdf_path_side.exists():
        with open(pdf_path_side, "rb") as f_pdf:
            pdf_bytes_side = f_pdf.read()
        st.download_button(
            label="📄 Baixar Mapa do Site (PDF)",
            data=pdf_bytes_side,
            file_name="mapa_do_site_adesampa.pdf",
            mime="application/pdf",
            key="dl_btn_sitemap_pdf_sidebar",
            use_container_width=True,
            help="Guia completo com capturas de tela fidedignas, catálogo dos 7 gráficos e roteiro de avaliação em 5 minutos para a banca."
        )

    st.markdown("---")
    st.markdown("### ⚙️ Opções do Mapa")
    mostrar_raio = st.checkbox("Exibir Raios de Cobertura (2.5 km)", value=True, help="Raio de atendimento estimado de cada Teia e FabLab")

    st.markdown("---")
    # Painel de Status de Conexão e Metadados do Sistema
    status_online = verificar_conexao_externa()
    if status_online:
        badge_cor = "#059669"
        badge_bg = "#ECFDF5"
        badge_border = "#A7F3D0"
        status_texto = "Online"
        status_emoji = "🟢"
        status_subtexto = "Conectado aos serviços de rede"
    else:
        badge_cor = "#DC2626"
        badge_bg = "#FEF2F2"
        badge_border = "#FECACA"
        status_texto = "Sem Conexão"
        status_emoji = "🔴"
        status_subtexto = "Operando em modo local offline"

    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #64748B; line-height: 1.5; padding: 4px 0;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 13px;">{status_emoji}</span>
            <span style="background-color: {badge_bg}; color: {badge_cor}; border: 1px solid {badge_border}; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 11.5px;">{status_texto}</span>
        </div>
        <div style="font-size: 0.74rem; color: #94A3B8; margin-bottom: 6px;">{status_subtexto}</div>
        <div><strong>Ambiente:</strong> Produção Local</div>
        <div><strong>Versão:</strong> v1.0.0 (Estável)</div>
        <div><strong>Bases:</strong> GeoSampa • PMSP • SEADE</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Recarregar Dados", use_container_width=True, help="Limpa o cache em memória e recarrega as bases do disco"):
        st.cache_data.clear()
        st.rerun()


# 4. Cabeçalho Principal (com Logotipo Oficial no canto superior esquerdo)
logo_b64 = carregar_logo_base64(str(LOGO_PATH))
img_tag = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="Logotipo ADE SAMPA" />' if logo_b64 else ''

st.markdown(f"""
<div class="main-header">
    <div class="header-content">
        {img_tag}
        <div>
            <div class="header-badge">🌐 Observatório de Inteligência Territorial</div>
            <h1>ADE SAMPA Territórios Inteligentes</h1>
            <p>Painel Integrado de Diagnóstico Geoespacial, Desertos de Fomento e Apoio à Tomada de Decisão Pública</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# 5. Métricas Resumo no Topo (BigNumbers com Texto Alternativo e Acessibilidade WCAG)
col1, col2, col3, col4, col5 = st.columns(5)

kpi_data = [
    {
        "label": "População Total",
        "value": f"{metricas_cidade['populacao_total']:,}".replace(",", ".") + " hab",
        "alt_text": "96 distritos paulistanos",
        "aria_label": f"População total de {metricas_cidade['populacao_total']} habitantes distribuídos nos 96 distritos de São Paulo",
        "title": "Estimativa populacional oficial consolidada via Censo Demográfico e SEADE",
        "icon": "👥",
        "accent": "#2563EB"
    },
    {
        "label": "Renda Média Formal",
        "value": f"R$ {metricas_cidade['renda_media_cidade']:,.2f}",
        "alt_text": "Remuneração média formal",
        "aria_label": f"Renda média formal de R$ {metricas_cidade['renda_media_cidade']:.2f} na capital paulista",
        "title": "Remuneração média dos vínculos de emprego formais (RAIS / Caged)",
        "icon": "💼",
        "accent": "#0D9488"
    },
    {
        "label": "Deslocamento Médio",
        "value": f"{metricas_cidade['tempo_medio_deslocamento']} min",
        "alt_text": "Trânsito casa-trabalho",
        "aria_label": f"Tempo médio de deslocamento de {metricas_cidade['tempo_medio_deslocamento']} minutos até o local de trabalho",
        "title": "Média de tempo diário gasto em transporte público ou individual para trabalhar",
        "icon": "⏱️",
        "accent": "#0284C7"
    },
    {
        "label": "Equipamentos ADE SAMPA",
        "value": f"{metricas_cidade['total_equipamentos']} unidades",
        "alt_text": "Teias, FabLabs e Postos",
        "aria_label": f"{metricas_cidade['total_equipamentos']} unidades ativas de fomento ao empreendedorismo da ADE SAMPA",
        "title": "Rede de coworkings Teia, laboratórios de fabricação digital FabLabs e postos de atendimento",
        "icon": "🏢",
        "accent": "#8B5CF6"
    },
    {
        "label": "Desertos Críticos",
        "value": f"{metricas_cidade['desertos_criticos_qtd']} distritos",
        "alt_text": "IDF ≥ 7.5 (Alta urgência)",
        "aria_label": f"{metricas_cidade['desertos_criticos_qtd']} distritos classificados como desertos críticos com índice IDF maior ou igual a 7.5",
        "title": "Territórios periféricos com alta carência de fomento, longa viagem e baixa renda",
        "icon": "🚨",
        "accent": "#EF4444"
    }
]

for col, kpi in zip([col1, col2, col3, col4, col5], kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" 
             style="border-top: 4px solid {kpi['accent']};"
             role="region"
             aria-label="{kpi['aria_label']}" 
             title="{kpi['title']}">
            <div class="kpi-header">
                <span class="kpi-label">{kpi['label']}</span>
                <span class="kpi-icon" aria-hidden="true">{kpi['icon']}</span>
            </div>
            <div class="kpi-value">{kpi['value']}</div>
            <div class="kpi-alt-text" aria-hidden="true">
                <span class="kpi-alt-dot" style="background-color: {kpi['accent']};"></span>
                <span>{kpi['alt_text']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# 6. Navegação em Abas
aba_mapa, aba_ia, aba_graficos, aba_equipamentos, aba_metodologia = st.tabs([
    "🗺️ Mapa Territorial Interativo",
    "🤖 Copiloto de IA & Diagnóstico",
    "📈 Observatório Comparativo",
    "🏢 Rede de Equipamentos ADE SAMPA",
    "📑 Metodologia & Edital"
])


# -------------------------------------------------------------
# ABA 1: MAPA TERRITORIAL
# -------------------------------------------------------------
with aba_mapa:
    st.markdown("#### Distribuição Territorial e Pontos Cegos de Cobertura")
    st.caption("Passe o cursor sobre os distritos para visualizar indicadores. Cores mais quentes (vermelho/laranja) indicam maior urgência de novos investimentos.")

    # Legenda Explicativa: Vulnerabilidade dos Distritos e Ícones dos Equipamentos ADE SAMPA
    with st.container():
        st.markdown(
            "<div style='font-size: 11.5px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;'>"
            "🎨 Vulnerabilidade Territorial dos Distritos (Cores dos Polígonos / IDF):"
            "</div>",
            unsafe_allow_html=True
        )
        c_v1, c_v2, c_v3, c_v4 = st.columns(4)
        with c_v1:
            st.markdown("🔴 **Deserto Crítico** (IDF ≥ 7.5)<br><span style='font-size: 0.78rem; color: #64748B;'>Ação urgente / Carência severa</span>", unsafe_allow_html=True)
        with c_v2:
            st.markdown("🟡 **Deserto Moderado** (IDF 5.5 a 7.4)<br><span style='font-size: 0.78rem; color: #64748B;'>Expansão / Transição</span>", unsafe_allow_html=True)
        with c_v3:
            st.markdown("🔵 **Em Cobertura** (IDF 3.5 a 5.4)<br><span style='font-size: 0.78rem; color: #64748B;'>Monitoramento territorial</span>", unsafe_allow_html=True)
        with c_v4:
            st.markdown("🟢 **Polo Consolidado** (IDF &lt; 3.5)<br><span style='font-size: 0.78rem; color: #64748B;'>Estruturado / Econômico</span>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 10px; margin-bottom: 6px; font-size: 11.5px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;'>🏢 O que é cada Ícone de Equipamento no Mapa:</div>", unsafe_allow_html=True)
        c_eq1, c_eq2, c_eq3, c_eq4 = st.columns(4)
        with c_eq1:
            st.markdown(
                "<div style='background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 10px 12px; min-height: 95px;'>"
                "<div style='font-weight: 700; color: #1D4ED8; font-size: 12.5px; margin-bottom: 3px;'>💻 Rede Teia (Laptop Azul)</div>"
                "<div style='font-size: 11.5px; color: #334155; line-height: 1.35;'>Coworking público gratuito com internet rápida, computadores livres e oficinas.</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with c_eq2:
            st.markdown(
                "<div style='background: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 10px; padding: 10px 12px; min-height: 95px;'>"
                "<div style='font-weight: 700; color: #6D28D9; font-size: 12.5px; margin-bottom: 3px;'>🧊 FabLab Livre (Cubo Roxo)</div>"
                "<div style='font-size: 11.5px; color: #334155; line-height: 1.35;'>Fabricação digital, impressoras 3D, cortadoras a laser e prototipagem.</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with c_eq3:
            st.markdown(
                "<div style='background: #FFF7ED; border: 1px solid #FED7AA; border-radius: 10px; padding: 10px 12px; min-height: 95px;'>"
                "<div style='font-weight: 700; color: #C2410C; font-size: 12.5px; margin-bottom: 3px;'>💼 Posto ADE SAMPA (Maleta)</div>"
                "<div style='font-size: 11.5px; color: #334155; line-height: 1.35;'>Atendimento presencial, MEI, cursos e orientação para microcrédito.</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with c_eq4:
            st.markdown(
                "<div style='background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 10px; padding: 10px 12px; min-height: 95px;'>"
                "<div style='font-weight: 700; color: #0284C7; font-size: 12.5px; margin-bottom: 3px;'>⭕ Raio 2.5 km (Círculo Azul)</div>"
                "<div style='font-size: 11.5px; color: #334155; line-height: 1.35;'>Alcance territorial estimado de atendimento a pé/transporte local.</div>"
                "</div>",
                unsafe_allow_html=True
            )
        st.markdown("<div style='font-size: 11px; color: #64748B; font-style: italic; margin-top: 6px; margin-bottom: 12px;'>🎙️ <strong>Estúdio Sampa Cast:</strong> Unidades selecionadas contam com estrutura acústica e equipamentos para criação e gravação de podcasts.</div>", unsafe_allow_html=True)

    distritos_destacados = df_filtrado["distrito"].tolist()
    filtro_ativo = len(distritos_destacados) < len(df_indicadores)

    if filtro_ativo:
        total_eq_filtro = int(df_filtrado["equipamentos_adesampa_ativos"].sum())
        status_eq = (
            f"**{total_eq_filtro} unidade(s) ativa(s)**"
            if total_eq_filtro > 0
            else "**0 unidades ativas (Ponto Cego de Cobertura / Deserto)**"
        )
        sub_info = f" • Subprefeitura: **{sub_sel}**" if sub_sel != "Todas" else ""
        zona_info = f" • Zona: **{zona_sel}**" if zona_sel != "Todas" else ""
        st.info(
            f"🎯 **Sincronização Territorial Ativa:** Exibindo **{len(df_filtrado)} distritos** destacados no mapa e na tabela{zona_info}{sub_info}. "
            f"Equipamentos ADE SAMPA na seleção: {status_eq}. O mapa aproximou o enquadramento na área selecionada.",
            icon="📍"
        )

    # Renderização do Mapa Folium com sincronização dinâmica de distritos e enquadramento
    mapa_gerado = criar_mapa_territorial(
        geojson_distritos=geojson_distritos,
        equipamentos=equipamentos,
        mostrar_raio_cobertura=mostrar_raio,
        distritos_destacados=distritos_destacados,
        focar_selecao=True
    )
    st_folium(mapa_gerado, width="100%", height=560, returned_objects=[])

    st.markdown("---")
    col_tab_tit, col_tab_dl = st.columns([3, 1.3])
    with col_tab_tit:
        st.markdown(f"##### 📋 Distritos em Destaque na Seleção Atual ({len(df_filtrado)} distritos)")
    with col_tab_dl:
        st.download_button(
            label="📥 Baixar Seleção (CSV)",
            data=csv_filtrado_bytes,
            file_name=nome_csv_filtrado,
            mime="text/csv",
            key="dl_btn_aba1",
            use_container_width=True,
            help="Exporta a planilha dos distritos selecionados com todos os indicadores em formato CSV (compatível com Excel)."
        )

    st.dataframe(
        df_exportar,
        use_container_width=True,
        hide_index=True
    )


# -------------------------------------------------------------
# ABA 2: COPILOTO DE IA & DIAGNÓSTICO
# -------------------------------------------------------------
with aba_ia:
    st.markdown("#### 🤖 Diagnóstico Territorial Automatizado com IA")
    st.markdown("Selecione qualquer um dos 96 distritos de São Paulo para que o copiloto analítico gere um **parecer técnico estruturado com recomendações de alocação de programas da ADE SAMPA**.")

    col_sel_distrito, col_info_rapida = st.columns([1, 2])

    with col_sel_distrito:
        distritos_ordenados = sorted(list(df_indicadores["distrito"].unique()))
        # Sugestão padrão em distrito crítico periférico
        idx_padrao = distritos_ordenados.index("Brasilândia") if "Brasilândia" in distritos_ordenados else 0
        distrito_escolhido = st.selectbox("Selecione o Distrito para Análise:", distritos_ordenados, index=idx_padrao)

        dados_distrito = df_indicadores[df_indicadores["distrito"] == distrito_escolhido].iloc[0].to_dict()
        equipamentos_locais = buscar_equipamentos_por_distrito(equipamentos, distrito_escolhido)

        st.markdown(f"""
        <div class="metric-card">
            <h4>{dados_distrito['distrito']}</h4>
            <p><strong>Subprefeitura:</strong> {dados_distrito['subprefeitura']}</p>
            <p><strong>Zona:</strong> {dados_distrito['zona']}</p>
            <p><strong>População:</strong> {dados_distrito['populacao']:,}</p>
            <p><strong>Renda Média:</strong> R$ {dados_distrito['renda_media_formal']:,.2f}</p>
            <p><strong>Tempo ao Trabalho:</strong> {dados_distrito['tempo_deslocamento_min']:.1f} min</p>
            <p><strong>Equipamentos Ativos:</strong> {len(equipamentos_locais)}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Regenerar Parecer Técnico", type="primary", use_container_width=True):
            st.rerun()

    with col_info_rapida:
        # Geração do Diagnóstico pela IA
        resultado_ia = gerar_diagnostico_ia(dados_distrito)
        st.markdown(resultado_ia["relatorio_markdown"])

        # Download do relatório em markdown
        st.download_button(
            label="📥 Baixar Parecer Técnico (Markdown)",
            data=resultado_ia["relatorio_markdown"],
            file_name=f"parecer_tecnico_{distrito_escolhido.lower()}.md",
            mime="text/markdown"
        )


# -------------------------------------------------------------
# ABA 3: OBSERVATÓRIO COMPARATIVO
# -------------------------------------------------------------
with aba_graficos:
    st.markdown("#### 📈 Observatório Comparativo e Analítico de Disparidades")
    st.caption("Filtre por qualquer dimensão territorial, explore o studio dinâmico de mobilidade e selecione quais gráficos deseja renderizar.")

    sub_studio, sub_multidimensional = st.tabs([
        "⏱️ Studio Dinâmico de Mobilidade (Tempo ao Trabalho)",
        "📊 Observatório Multidimensional & Filtros Livres"
    ])

    # =========================================================
    # SUB-ABA 1: STUDIO DINÂMICO DE MOBILIDADE
    # =========================================================
    with sub_studio:
        st.markdown("##### 🎨 Studio Construtor de Gráficos (Eixos X & Y Customizáveis)")
        st.caption("Personalize sua análise: escolha livremente o tipo de gráfico, quais indicadores ocuparão os eixos X e Y, o sentido da ordenação (ascendente ou decrescente), a amostra de bairros e a região da capital. Confirme sua seleção com a tecla Enter ou no botão.")

        # Dicionário de campos disponíveis com labels intuitivas
        CAMPOS_STUDIO = {
            "Distrito / Bairro": "distrito",
            "Tempo de Ida ao Trabalho (min)": "tempo_deslocamento_min",
            "Renda Média Formal (R$)": "renda_media_formal",
            "Índice de Deserto de Fomento (IDF)": "indice_deserto_fomento",
            "População Estimada": "populacao",
            "Oferta de Empregos (por 100 hab)": "empregos_por_100hab",
            "Equipamentos ADE SAMPA Ativos": "equipamentos_adesampa_ativos",
            "Zona / Região da Capital": "zona",
            "Subprefeitura": "subprefeitura",
            "Classificação de Vulnerabilidade": "classificacao_vulnerabilidade"
        }

        # Inicialização do estado seguro
        if "studio_custom_config" not in st.session_state:
            st.session_state["studio_custom_config"] = {
                "tipo": "📈 Gráfico de Linhas (com marcadores)",
                "eixo_x": "Distrito / Bairro",
                "eixo_y": "Tempo de Ida ao Trabalho (min)",
                "ordem": "⬇️ Decrescente (Maior ao menor)",
                "ordenar_por": "Eixo Y (Indicador Vertical)",
                "qtd": "Top 15 distritos",
                "zona": "Todas as Zonas",
                "colorir_zona": True
            }

        lista_tipos_graficos = [
            "📈 Gráfico de Linhas (com marcadores)",
            "📊 Gráfico de Barras Horizontais",
            "📶 Gráfico de Barras Verticais",
            "🍭 Gráfico de Pirulito (Lollipop)",
            "📉 Gráfico de Área Preenchida",
            "🥧 Gráfico de Pizza / Donut",
            "📍 Gráfico de Dispersão (Scatter)"
        ]

        tipo_salvo = st.session_state["studio_custom_config"].get("tipo", lista_tipos_graficos[0])
        idx_tipo_inicial = lista_tipos_graficos.index(tipo_salvo) if tipo_salvo in lista_tipos_graficos else 0

        # 1. Seletor do Modelo Visual fora do form para adaptação dinâmica imediata
        col_tipo_head, col_tipo_badge = st.columns([1.6, 2.4])
        with col_tipo_head:
            tipo_graf_sel = st.selectbox(
                "📊 1. Escolha o Tipo de Gráfico:",
                lista_tipos_graficos,
                index=idx_tipo_inicial,
                key="studio_tipo_graf_sel",
                help="Escolha o modelo de visualização. Os controles de eixos e ordenação se ajustam automaticamente às propriedades do gráfico."
            )

        # Verificação metodológica por estilo de gráfico:
        # - Linhas, Barras Horizontais, Barras Verticais, Lollipop e Área: Sequenciais/Rankings -> Ordenação Ascendente/Decrescente ativa.
        # - Pizza / Donut: Gráfico de composição de parte-para-o-todo -> O objetivo é a distribuição geral; ordenação sequencial não se aplica.
        # - Dispersão (Scatter): Plano cartesiano bivariado -> Pontos fixos em coordenadas (X, Y); ordenação sequencial não se aplica.
        permite_ordenacao = any(t in tipo_graf_sel for t in ["Linhas", "Barras", "Pirulito", "Área"])
        is_pizza = "Pizza" in tipo_graf_sel
        is_scatter = "Dispersão" in tipo_graf_sel

        with col_tipo_badge:
            if permite_ordenacao:
                st.markdown(
                    "<div style='padding-top: 24px;'><span style='background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;'>"
                    "🔄 <strong>Ordenação Habilitada:</strong> Gráfico sequencial/ranking — suporta sentido Ascendente ou Decrescente.</span></div>",
                    unsafe_allow_html=True
                )
            elif is_pizza:
                st.markdown(
                    "<div style='padding-top: 24px;'><span style='background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;'>"
                    "🥧 <strong>Distribuição Geral:</strong> Gráfico de proporção/composição — sentido ascendente/decrescente não se aplica.</span></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='padding-top: 24px;'><span style='background-color: #F3E8FF; color: #6B21A8; border: 1px solid #E9D5FF; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;'>"
                    "📍 <strong>Plano Cartesiano:</strong> Posição dos pontos dada por coordenadas (X, Y) — ordenação sequencial não se aplica.</span></div>",
                    unsafe_allow_html=True
                )

        # 2. Formulário de parâmetros adaptativos com confirmação sob demanda (Enter físico e clique)
        with st.form("form_studio_personalizado"):
            col_f_x, col_f_y = st.columns(2)
            with col_f_x:
                label_x = "↔️ Categoria / Fatias (Eixo X):" if is_pizza else "↔️ Eixo X (Horizontal / Categoria):"
                eixo_x_sel = st.selectbox(
                    label_x,
                    list(CAMPOS_STUDIO.keys()),
                    index=0,
                    help="Defina a categoria ou campo para o eixo X / fatias."
                )
            with col_f_y:
                label_y = "↕️ Métrica / Valor da Fatia (Eixo Y):" if is_pizza else "↕️ Eixo Y (Vertical / Indicador):"
                eixo_y_sel = st.selectbox(
                    label_y,
                    list(CAMPOS_STUDIO.keys()),
                    index=1,
                    help="Defina a métrica quantitativa para o eixo Y / tamanho da fatia."
                )

            col_f_ordem, col_f_por, col_f_qtd, col_f_zona = st.columns([1.2, 1.2, 1.0, 1.0])
            with col_f_ordem:
                if permite_ordenacao:
                    ordem_sel = st.selectbox(
                        "🔄 Sentido da Ordenação:",
                        [
                            "⬇️ Decrescente (Maior ao menor)",
                            "⬆️ Ascendente (Menor ao maior)"
                        ],
                        index=0 if "Decrescente" in st.session_state["studio_custom_config"].get("ordem", "") else 1,
                        help="Ordem decrescente exibe valores maiores primeiro; ordem ascendente exibe menores primeiro."
                    )
                elif is_pizza:
                    ordem_sel = st.selectbox(
                        "🔄 Sentido da Ordenação:",
                        ["ℹ️ Não aplicável (Distribuição Geral)"],
                        index=0,
                        disabled=True,
                        help="Gráficos de Pizza mostram a proporção e distribuição geral do todo (100%); a ordenação sequencial ascendente/decrescente não se aplica."
                    )
                else:  # Dispersão
                    ordem_sel = st.selectbox(
                        "🔄 Sentido da Ordenação:",
                        ["ℹ️ Não aplicável (Coordenadas X, Y)"],
                        index=0,
                        disabled=True,
                        help="Em gráficos de dispersão, a posição espacial de cada ponto é estritamente definida pelas coordenadas (X, Y) no plano cartesiano."
                    )

            with col_f_por:
                if permite_ordenacao:
                    ordenar_por_sel = st.selectbox(
                        "🎯 Ordenar Por:",
                        [
                            "Eixo Y (Indicador Vertical)",
                            "Eixo X (Horizontal / Categoria)",
                            "Ordem Alfabética do Distrito"
                        ],
                        index=0,
                        help="Escolha qual dos eixos determinará a ordenação dos dados."
                    )
                elif is_pizza:
                    ordenar_por_sel = st.selectbox(
                        "🎯 Ordenar Por:",
                        ["ℹ️ Proporção das Fatias (360°)"],
                        index=0,
                        disabled=True,
                        help="Distribuição angular proporcional automática conforme o valor da fatia."
                    )
                else:
                    ordenar_por_sel = st.selectbox(
                        "🎯 Ordenar Por:",
                        ["ℹ️ Coordenadas Cartesianas (X, Y)"],
                        index=0,
                        disabled=True,
                        help="Plotagem bivariada direta nos eixos contínuos."
                    )

            with col_f_qtd:
                qtd_sel = st.selectbox(
                    "🔢 Amostra de Distritos:",
                    ["Top 10 distritos", "Top 15 distritos", "Top 20 distritos", "Top 30 distritos", "Top 50 distritos", "Todos os 96 distritos"],
                    index=1,
                    help="Quantidade de distritos incluídos no gráfico."
                )
            with col_f_zona:
                zona_mob_sel = st.selectbox(
                    "📍 Região da Capital:",
                    ["Todas as Zonas", "Centro", "Leste", "Norte", "Oeste", "Sul"],
                    index=0,
                    help="Filtre os distritos por uma zona específica ou analise toda a capital."
                )

            col_sub_opt, col_sub_btn = st.columns([2.3, 1.7])
            with col_sub_opt:
                colorir_zona_sel = st.checkbox(
                    "🎨 Colorir elementos por Zona da Capital",
                    value=True,
                    help="Aplica cores temáticas da capital para facilitar a identificação das regiões."
                )
            with col_sub_btn:
                btn_gerar_grafico = st.form_submit_button(
                    "🚀 Gerar Gráfico (Enter ↵)",
                    type="primary",
                    use_container_width=True
                )

        if btn_gerar_grafico:
            st.session_state["studio_custom_config"] = {
                "tipo": tipo_graf_sel,
                "eixo_x": eixo_x_sel,
                "eixo_y": eixo_y_sel,
                "ordem": ordem_sel,
                "ordenar_por": ordenar_por_sel,
                "qtd": qtd_sel,
                "zona": zona_mob_sel,
                "colorir_zona": colorir_zona_sel
            }

        cfg_atual = st.session_state["studio_custom_config"]
        # Mantém sincronizado com a seleção do tipo de gráfico no topo
        if cfg_atual.get("tipo") != tipo_graf_sel:
            cfg_atual["tipo"] = tipo_graf_sel

        col_x = CAMPOS_STUDIO[cfg_atual["eixo_x"]]
        col_y = CAMPOS_STUDIO[cfg_atual["eixo_y"]]
        is_x_num = pd.api.types.is_numeric_dtype(df_indicadores[col_x])
        is_y_num = pd.api.types.is_numeric_dtype(df_indicadores[col_y])

        # Filtragem de zona
        df_mob = df_indicadores.copy()
        if cfg_atual["zona"] != "Todas as Zonas":
            df_mob = df_mob[df_mob["zona"] == cfg_atual["zona"]].copy()

        # Ordenação de acordo com a capacidade do estilo de gráfico
        is_ascendente = "Ascendente" in cfg_atual.get("ordem", "")
        if permite_ordenacao:
            if cfg_atual.get("ordenar_por") == "Eixo Y (Indicador Vertical)":
                campo_sort = col_y
            elif cfg_atual.get("ordenar_por") == "Eixo X (Horizontal / Categoria)":
                campo_sort = col_x
            else:
                campo_sort = "distrito"
            df_mob = df_mob.sort_values(by=campo_sort, ascending=is_ascendente)
        elif is_pizza:
            # Em Pizza, ordenamos decrescente apenas para estruturar o início do círculo pelas fatias de maior peso
            val_col = col_y if is_y_num else (col_x if is_x_num else "populacao")
            df_mob = df_mob.sort_values(by=val_col, ascending=False)
        else:
            # Em Dispersão (Scatter), pontos são desenhados diretamente em (X, Y)
            val_col = col_y if is_y_num else col_x
            df_mob = df_mob.sort_values(by=val_col, ascending=False)

        # Fatiamento Top N
        if "10" in cfg_atual["qtd"]:
            limite_n = 10
        elif "15" in cfg_atual["qtd"]:
            limite_n = 15
        elif "20" in cfg_atual["qtd"]:
            limite_n = 20
        elif "30" in cfg_atual["qtd"]:
            limite_n = 30
        elif "50" in cfg_atual["qtd"]:
            limite_n = 50
        else:
            limite_n = len(df_mob)

        df_mob_plot = df_mob.head(limite_n).copy()

        if len(df_mob_plot) == 0:
            st.warning("⚠️ Nenhum distrito encontrado para os parâmetros selecionados.")
        else:
            # Cards de Síntese Analítica adaptativos
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)

            # Identifica a métrica principal para o KPI (prioriza Y se for numérico, senão X)
            metrica_kpi = col_y if is_y_num else (col_x if is_x_num else None)
            label_kpi = cfg_atual["eixo_y"] if is_y_num else (cfg_atual["eixo_x"] if is_x_num else "Distritos")

            if metrica_kpi is not None:
                val_max = float(df_mob_plot[metrica_kpi].max())
                val_min = float(df_mob_plot[metrica_kpi].min())
                val_med = float(df_mob_plot[metrica_kpi].mean())
                dist_max = df_mob_plot.loc[df_mob_plot[metrica_kpi] == val_max, "distrito"].iloc[0]
                dist_min = df_mob_plot.loc[df_mob_plot[metrica_kpi] == val_min, "distrito"].iloc[0]
                razao_disp = val_max / val_min if val_min > 0 else 1.0

                if "renda" in metrica_kpi:
                    fmt_max, fmt_min, fmt_med = f"R$ {val_max:,.2f}", f"R$ {val_min:,.2f}", f"R$ {val_med:,.2f}"
                elif "populacao" in metrica_kpi:
                    fmt_max, fmt_min, fmt_med = f"{val_max:,.0f} hab", f"{val_min:,.0f} hab", f"{val_med:,.0f} hab"
                elif "tempo" in metrica_kpi:
                    fmt_max, fmt_min, fmt_med = f"{val_max:.1f} min", f"{val_min:.1f} min", f"{val_med:.1f} min"
                else:
                    fmt_max, fmt_min, fmt_med = f"{val_max:.2f}", f"{val_min:.2f}", f"{val_med:.2f}"

                with k1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Maior {label_kpi[:15]}</span><span class="kpi-icon">🔝</span></div>
                        <div class="kpi-value">{fmt_max}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #DC2626;"></span>{dist_max}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Menor {label_kpi[:15]}</span><span class="kpi-icon">🔻</span></div>
                        <div class="kpi-value">{fmt_min}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #059669;"></span>{dist_min}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Média da Amostra</span><span class="kpi-icon">📊</span></div>
                        <div class="kpi-value">{fmt_med}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #2563EB;"></span>{len(df_mob_plot)} distritos</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k4:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Disparidade (Máx/Mín)</span><span class="kpi-icon">⚖️</span></div>
                        <div class="kpi-value">{razao_disp:.1f}x</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #D97706;"></span>Razão Territorial</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with k1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Amostra</span><span class="kpi-icon">📍</span></div>
                        <div class="kpi-value">{len(df_mob_plot)}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #2563EB;"></span>Distritos</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">População Total</span><span class="kpi-icon">👥</span></div>
                        <div class="kpi-value">{df_mob_plot["populacao"].sum():,.0f}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #059669;"></span>Habitantes</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Zonas Presentes</span><span class="kpi-icon">🏙️</span></div>
                        <div class="kpi-value">{df_mob_plot["zona"].nunique()}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #D97706;"></span>Regiões</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k4:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-header"><span class="kpi-label">Equipamentos ADE SAMPA</span><span class="kpi-icon">🏢</span></div>
                        <div class="kpi-value">{df_mob_plot["equipamentos_adesampa_ativos"].sum()}</div>
                        <div class="kpi-alt-text"><span class="kpi-alt-dot" style="background-color: #8B5CF6;"></span>Unidades Ativas</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

            cores_zonas = {
                "Centro": "#10B981",
                "Oeste": "#06B6D4",
                "Norte": "#F59E0B",
                "Leste": "#EF4444",
                "Sul": "#8B5CF6"
            }

            estilo_hover = dict(
                bgcolor="#FFFFFF",
                font_size=13,
                font_family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
                font_color="#0F172A",
                bordercolor="#CBD5E1"
            )

            tipo_escolhido = cfg_atual["tipo"]
            direcao_str = "geral"
            if permite_ordenacao:
                direcao_str = "Ascendente" if is_ascendente else "Decrescente"
                titulo_graf = f"{cfg_atual['eixo_y']} vs {cfg_atual['eixo_x']} ({direcao_str} • {len(df_mob_plot)} distritos)"
            elif is_pizza:
                direcao_str = "Proporcional"
                titulo_graf = f"Distribuição Geral Proporcional: {cfg_atual['eixo_y']} por {cfg_atual['eixo_x']} ({len(df_mob_plot)} distritos)"
            else:
                direcao_str = "Cartesiana"
                titulo_graf = f"Dispersão Cartesiana: {cfg_atual['eixo_y']} vs {cfg_atual['eixo_x']} ({len(df_mob_plot)} distritos)"
            colorir = cfg_atual["colorir_zona"]

            # 1. LINHAS
            if "Linhas" in tipo_escolhido:
                fig_mob = px.line(
                    df_mob_plot,
                    x=col_x,
                    y=col_y,
                    markers=True,
                    labels={col_x: cfg_atual["eixo_x"], col_y: cfg_atual["eixo_y"], "zona": "Zona"},
                    title=titulo_graf,
                    custom_data=["distrito", "zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "populacao"]
                )
                fig_mob.update_traces(
                    line=dict(color="#2563EB", width=3),
                    marker=dict(size=8, color="#1D4ED8", symbol="circle"),
                    hovertemplate=(
                        "<b>📍 Distrito: %{customdata[0]}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        f"• <b>{cfg_atual['eixo_x']}:</b> %{{x}}<br>"
                        f"• <b>{cfg_atual['eixo_y']}:</b> %{{y}}<br>"
                        "• <b>Região:</b> Zona %{customdata[1]} | Subprefeitura: %{customdata[2]}<br>"
                        "• <b>Renda Média:</b> R$ %{customdata[3]:,.2f}<br>"
                        "• <b>Tempo Deslocamento:</b> %{customdata[4]:.1f} min<br>"
                        "• <b>População:</b> %{customdata[5]:,.0f} hab<br>"
                        "<extra></extra>"
                    )
                )
                if col_x in ["distrito", "zona", "subprefeitura", "classificacao_vulnerabilidade"]:
                    fig_mob.update_xaxes(
                        categoryorder="array",
                        categoryarray=df_mob_plot[col_x].tolist(),
                        tickangle=-45 if len(df_mob_plot) > 10 else 0
                    )

            # 2. BARRAS HORIZONTAIS
            elif "Barras Horizontais" in tipo_escolhido:
                fig_mob = px.bar(
                    df_mob_plot,
                    x=col_x,
                    y=col_y,
                    orientation="h",
                    color="zona" if colorir else None,
                    color_discrete_map=cores_zonas if colorir else None,
                    labels={col_x: cfg_atual["eixo_x"], col_y: cfg_atual["eixo_y"], "zona": "Zona"},
                    title=titulo_graf,
                    custom_data=["distrito", "zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "populacao"]
                )
                if col_y in ["distrito", "zona", "subprefeitura", "classificacao_vulnerabilidade"]:
                    ordem_y = df_mob_plot[col_y].tolist()[::-1]
                    fig_mob.update_yaxes(categoryorder="array", categoryarray=ordem_y)
                fig_mob.update_traces(
                    hovertemplate=(
                        "<b>📍 Distrito: %{customdata[0]}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        f"• <b>{cfg_atual['eixo_y']}:</b> %{{y}}<br>"
                        f"• <b>{cfg_atual['eixo_x']}:</b> %{{x}}<br>"
                        "• <b>Região:</b> Zona %{customdata[1]}<br>"
                        "• <b>Subprefeitura:</b> %{customdata[2]}<br>"
                        "<extra></extra>"
                    )
                )

            # 3. BARRAS VERTICAIS
            elif "Barras Verticais" in tipo_escolhido:
                fig_mob = px.bar(
                    df_mob_plot,
                    x=col_x,
                    y=col_y,
                    color="zona" if colorir else None,
                    color_discrete_map=cores_zonas if colorir else None,
                    labels={col_x: cfg_atual["eixo_x"], col_y: cfg_atual["eixo_y"], "zona": "Zona"},
                    title=titulo_graf,
                    custom_data=["distrito", "zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "populacao"]
                )
                if col_x in ["distrito", "zona", "subprefeitura", "classificacao_vulnerabilidade"]:
                    fig_mob.update_xaxes(
                        categoryorder="array",
                        categoryarray=df_mob_plot[col_x].tolist(),
                        tickangle=-45 if len(df_mob_plot) > 10 else 0
                    )
                fig_mob.update_traces(
                    hovertemplate=(
                        "<b>📍 Distrito: %{customdata[0]}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        f"• <b>{cfg_atual['eixo_x']}:</b> %{{x}}<br>"
                        f"• <b>{cfg_atual['eixo_y']}:</b> %{{y}}<br>"
                        "• <b>Região:</b> Zona %{customdata[1]}<br>"
                        "<extra></extra>"
                    )
                )

            # 4. PIZZA / DONUT
            elif "Pizza" in tipo_escolhido:
                if len(df_mob_plot) > 8:
                    st.info(f"💡 Para manter clareza e legibilidade visual das fatias, o gráfico de Pizza exibe os {min(8, len(df_mob_plot))} distritos mais expressivos da seleção.")
                    df_pie_mob = df_mob_plot.head(8).copy()
                else:
                    df_pie_mob = df_mob_plot.copy()

                pie_names = col_x if not is_x_num else col_y
                pie_values = col_y if is_y_num else (col_x if is_x_num else "populacao")

                fig_mob = px.pie(
                    df_pie_mob,
                    names=pie_names,
                    values=pie_values,
                    title=titulo_graf,
                    hole=0.42,
                    custom_data=["zona"]
                )
                fig_mob.update_traces(
                    texttemplate="<b>%{label}</b><br>%{value} (%{percent})",
                    textposition="inside",
                    textfont=dict(size=12, color="#FFFFFF"),
                    hovertemplate=(
                        "<b>📍 Item: %{label}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        "• <b>Valor:</b> %{value}<br>"
                        "• <b>Participação:</b> %{percent}<br>"
                        "• <b>Região:</b> Zona %{customdata[0]}<br>"
                        "<extra></extra>"
                    )
                )

            # 5. ÁREA PREENCHIDA
            elif "Área" in tipo_escolhido:
                fig_mob = px.area(
                    df_mob_plot,
                    x=col_x,
                    y=col_y,
                    labels={col_x: cfg_atual["eixo_x"], col_y: cfg_atual["eixo_y"]},
                    title=titulo_graf,
                    custom_data=["distrito", "zona", "subprefeitura"]
                )
                fig_mob.update_traces(
                    line=dict(color="#2563EB", width=2.5),
                    markers=True,
                    marker=dict(size=7, color="#1D4ED8"),
                    hovertemplate=(
                        "<b>📍 Distrito: %{customdata[0]}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        f"• <b>{cfg_atual['eixo_x']}:</b> %{{x}}<br>"
                        f"• <b>{cfg_atual['eixo_y']}:</b> %{{y}}<br>"
                        "<extra></extra>"
                    )
                )
                if col_x in ["distrito", "zona", "subprefeitura", "classificacao_vulnerabilidade"]:
                    fig_mob.update_xaxes(
                        categoryorder="array",
                        categoryarray=df_mob_plot[col_x].tolist(),
                        tickangle=-45 if len(df_mob_plot) > 10 else 0
                    )

            # 6. DISPERSÃO (SCATTER)
            elif "Dispersão" in tipo_escolhido:
                fig_mob = px.scatter(
                    df_mob_plot,
                    x=col_x,
                    y=col_y,
                    color="zona" if colorir else None,
                    color_discrete_map=cores_zonas if colorir else None,
                    hover_name="distrito",
                    labels={col_x: cfg_atual["eixo_x"], col_y: cfg_atual["eixo_y"], "zona": "Zona"},
                    title=titulo_graf,
                    custom_data=["distrito", "zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "populacao"]
                )
                fig_mob.update_traces(
                    marker=dict(size=12, line=dict(width=1.5, color="#FFFFFF")),
                    hovertemplate=(
                        "<b>📍 Distrito: %{hovertext}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        f"• <b>{cfg_atual['eixo_x']}:</b> %{{x}}<br>"
                        f"• <b>{cfg_atual['eixo_y']}:</b> %{{y}}<br>"
                        "• <b>Região:</b> Zona %{customdata[1]} | Subprefeitura: %{customdata[2]}<br>"
                        "• <b>Renda Média:</b> R$ %{customdata[3]:,.2f}<br>"
                        "• <b>Tempo Deslocamento:</b> %{customdata[4]:.1f} min<br>"
                        "<extra></extra>"
                    )
                )

            # 7. PIRULITO (LOLLIPOP)
            else:
                fig_mob = go.Figure()
                x_val_col = col_x if is_x_num else col_y
                y_cat_col = col_y if not is_x_num else col_x

                for _, r in df_mob_plot.iterrows():
                    cor_haste = cores_zonas.get(r["zona"], "#2563EB") if colorir else "#2563EB"
                    fig_mob.add_shape(
                        type="line",
                        x0=0,
                        x1=r[x_val_col] if is_x_num else r[y_cat_col],
                        y0=r[y_cat_col] if not is_x_num else r[x_val_col],
                        y1=r[y_cat_col] if not is_x_num else r[x_val_col],
                        line=dict(color=cor_haste, width=2.5)
                    )
                fig_mob.add_trace(
                    go.Scatter(
                        x=df_mob_plot[x_val_col] if is_x_num else df_mob_plot[y_cat_col],
                        y=df_mob_plot[y_cat_col] if not is_x_num else df_mob_plot[x_val_col],
                        mode="markers+text",
                        marker=dict(
                            size=13,
                            color=[cores_zonas.get(z, "#2563EB") for z in df_mob_plot["zona"]] if colorir else "#2563EB",
                            line=dict(color="#FFFFFF", width=1.5)
                        ),
                        text=df_mob_plot[x_val_col].apply(lambda v: f" {v:.1f}" if isinstance(v, float) else f" {v}"),
                        textposition="middle right",
                        textfont=dict(size=11, color="#1E293B"),
                        customdata=df_mob_plot[["distrito", "zona", "subprefeitura"]].values,
                        hovertemplate=(
                            "<b>📍 Distrito: %{customdata[0]}</b><br>"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                            "• <b>Valor:</b> %{x}<br>"
                            "• <b>Região:</b> Zona %{customdata[1]} | Subprefeitura: %{customdata[2]}<br>"
                            "<extra></extra>"
                        )
                    )
                )
                if y_cat_col in ["distrito", "zona", "subprefeitura"]:
                    ordem_y = df_mob_plot[y_cat_col].tolist()[::-1]
                    fig_mob.update_yaxes(categoryorder="array", categoryarray=ordem_y)
                fig_mob.update_layout(title=titulo_graf)

            fig_mob.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                hoverlabel=estilo_hover,
                margin=dict(l=30, r=30, t=55, b=65),
                height=550 if len(df_mob_plot) <= 20 else max(550, len(df_mob_plot) * 24),
                title=dict(font=dict(size=18, color="#0F172A", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")),
                legend=dict(
                    font=dict(size=14, color="#0F172A"),
                    title_font=dict(size=15, color="#0F172A")
                )
            )
            fig_mob.update_xaxes(
                title_font=dict(size=16, color="#0F172A", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"),
                tickfont=dict(size=14, color="#1E293B", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")
            )
            fig_mob.update_yaxes(
                title_font=dict(size=16, color="#0F172A", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"),
                tickfont=dict(size=14, color="#1E293B", family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")
            )

            sufixo_download = direcao_str.lower() if "direcao_str" in locals() and direcao_str else "dados"
            nome_arquivo_base = f"adesampa_studio_{col_y}_{sufixo_download}"
            config_mob = obter_config_plotly_export(nome_arquivo_base)
            st.plotly_chart(fig_mob, use_container_width=True, config=config_mob)

            # Barra de Exportação Imediata: PNG de alta definição e dados tabulares CSV
            tab_dados = df_mob_plot[[
                "distrito", "zona", "subprefeitura", "tempo_deslocamento_min",
                "renda_media_formal", "populacao", "indice_deserto_fomento"
            ]].copy()
            tab_dados.columns = [
                "Distrito", "Zona", "Subprefeitura", "Tempo Deslocamento (min)",
                "Renda Média (R$)", "População", "Índice IDF"
            ]
            csv_bytes = tab_dados.to_csv(index=False, sep=";").encode("utf-8-sig")

            col_exp_png, col_exp_csv = st.columns([1, 1])
            with col_exp_png:
                st.download_button(
                    label="🖼️ Baixar Gráfico em Alta Resolução (PNG)",
                    data=lambda: exportar_figura_png(fig_mob),
                    file_name=f"{nome_arquivo_base}.png",
                    mime="image/png",
                    key="btn_dl_png_studio",
                    use_container_width=True,
                    help="Exporta a imagem do gráfico configurado em PNG de alta definição (300 DPI equivalente, ideal para relatórios e apresentações)."
                )
            with col_exp_csv:
                st.download_button(
                    label="📥 Baixar Dados Deste Gráfico (CSV)",
                    data=csv_bytes,
                    file_name=f"dados_grafico_personalizado_{sufixo_download}.csv",
                    mime="text/csv",
                    key="btn_dl_csv_studio",
                    use_container_width=True,
                    help="Exporta os dados deste gráfico estruturados para Excel / CSV."
                )

            # Tabela detalhada expansível
            with st.expander("📄 Ver Tabela com os Dados Detalhados Deste Gráfico", expanded=False):
                st.dataframe(
                    tab_dados.style.format({
                        "Tempo Deslocamento (min)": "{:.1f}",
                        "Renda Média (R$)": "R$ {:,.2f}",
                        "População": "{:,.0f}",
                        "Índice IDF": "{:.2f}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

    # =========================================================
    # SUB-ABA 2: OBSERVATÓRIO MULTIDIMENSIONAL & FILTROS LIVRES
    # =========================================================
    with sub_multidimensional:
        st.markdown("##### 🔍 Painel Multidimensional e Filtros Territoriais")
        st.caption("Filtre por qualquer dimensão territorial e selecione dinamicamente quais gráficos devem ser renderizados no painel.")

        # Painel Expansível de Controles Avançados e Seleção de Gráficos
        with st.expander("🎛️ Filtros Avançados por Campo & Seleção de Gráficos", expanded=True):
            col_ctrl_graf, col_ctrl_escopo = st.columns([3, 2])

        with col_ctrl_graf:
            opcoes_graficos = [
                "Abismo Centro x Periferia (Dispersão: Renda vs Deslocamento)",
                "Top Desertos de Fomento (Ranking de Urgência IDF)",
                "Distribuição de Equipamentos por Zona (Teias, FabLabs e Postos)",
                "Matriz de Vulnerabilidade Multidimensional (Renda x IDF x População)",
                "Tabela Comparativa Agregada por Subprefeitura"
            ]
            graficos_ativos = st.multiselect(
                "📊 Escolha quais gráficos devem aparecer na tela:",
                options=opcoes_graficos,
                default=[
                    "Abismo Centro x Periferia (Dispersão: Renda vs Deslocamento)",
                    "Top Desertos de Fomento (Ranking de Urgência IDF)",
                    "Distribuição de Equipamentos por Zona (Teias, FabLabs e Postos)"
                ],
                help="Selecione um ou mais gráficos para renderização simultânea no painel."
            )

        with col_ctrl_escopo:
            escopo_aplicacao = st.radio(
                "🎯 Escopo dos Filtros:",
                ["Aplicar filtros aos gráficos selecionados", "Exibir gráficos com a base completa (sem filtros)"],
                help="Defina se os gráficos abaixo refletirão a amostra filtrada ou a totalidade dos 96 distritos paulistanos."
            )

        st.markdown("---")
        st.markdown("##### 🔍 1. Filtros Territoriais e Políticas Públicas:")

        # Filtro de Zona da Capital em 5 colunas dedicadas (100% visível e acessível)
        st.markdown("📍 **Zona da Capital (Selecione as regiões para análise):**")
        cz1, cz2, cz3, cz4, cz5 = st.columns(5)
        with cz1:
            chk_centro = st.checkbox("🟢 Centro", value=True, key="filtro_chk_centro", help="Região Central (Sé, República, Bela Vista...)")
        with cz2:
            chk_leste = st.checkbox("🔴 Leste", value=True, key="filtro_chk_leste", help="Zona Leste (Itaquera, Guaianases, São Miguel...)")
        with cz3:
            chk_norte = st.checkbox("🟡 Norte", value=True, key="filtro_chk_norte", help="Zona Norte (Brasilândia, Santana, Freguesia do Ó...)")
        with cz4:
            chk_oeste = st.checkbox("🔵 Oeste", value=True, key="filtro_chk_oeste", help="Zona Oeste (Pinheiros, Lapa, Butantã...)")
        with cz5:
            chk_sul = st.checkbox("🟣 Sul", value=True, key="filtro_chk_sul", help="Zona Sul (Grajaú, Campo Limpo, Santo Amaro...)")

        zonas_obs = []
        if chk_centro: zonas_obs.append("Centro")
        if chk_leste: zonas_obs.append("Leste")
        if chk_norte: zonas_obs.append("Norte")
        if chk_oeste: zonas_obs.append("Oeste")
        if chk_sul: zonas_obs.append("Sul")
        if not zonas_obs:
            zonas_obs = ["Centro", "Leste", "Norte", "Oeste", "Sul"]

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        # Filtro de Classificação IDF em 4 colunas dedicadas (100% visível e acessível)
        st.markdown("🏷️ **Classificação de Deserto de Fomento (IDF):**")
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1:
            chk_critico = st.checkbox("🔴 Deserto Crítico (IDF ≥ 7.5)", value=True, key="filtro_chk_critico", help="Territórios de máxima urgência de novos postos e apoio")
        with cc2:
            chk_moderado = st.checkbox("🟡 Deserto Moderado (5.5 a 7.4)", value=True, key="filtro_chk_moderado", help="Áreas em expansão com carência intermediária")
        with cc3:
            chk_cobertura = st.checkbox("🔵 Em Cobertura (3.5 a 5.4)", value=True, key="filtro_chk_cobertura", help="Territórios sob monitoramento com cobertura regular")
        with cc4:
            chk_consolidado = st.checkbox("🟢 Polo Consolidado (< 3.5)", value=True, key="filtro_chk_consolidado", help="Polos econômicos já estruturados")

        classificacoes_prefixos = []
        if chk_critico: classificacoes_prefixos.append("Deserto Crítico")
        if chk_moderado: classificacoes_prefixos.append("Deserto Moderado")
        if chk_cobertura: classificacoes_prefixos.append("Em Cobertura")
        if chk_consolidado: classificacoes_prefixos.append("Polo Consolidado")
        if not classificacoes_prefixos:
            classificacoes_prefixos = ["Deserto Crítico", "Deserto Moderado", "Em Cobertura", "Polo Consolidado"]

        classificacoes_obs = [
            v for v in df_indicadores["classificacao_vulnerabilidade"].unique()
            if any(v.startswith(pref) for pref in classificacoes_prefixos)
        ]

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        # Filtro de Subprefeituras com modo amplo e desimpedido
        subs_disponiveis = sorted(list(df_indicadores[df_indicadores["zona"].isin(zonas_obs)]["subprefeitura"].unique()))
        col_sub_m, col_sub_s = st.columns([1.2, 2.8])
        with col_sub_m:
            st.markdown("🏢 **Subprefeituras:**")
            todas_subs = st.checkbox(
                f"Selecionar Todas ({len(subs_disponiveis)} subprefeituras)",
                value=True,
                key="filtro_todas_as_subs",
                help="Desmarque caso queira escolher subprefeituras específicas na lista ao lado"
            )

        with col_sub_s:
            if todas_subs:
                subprefeituras_obs = subs_disponiveis
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 14px; font-size: 13px; color: #475569; margin-top: 14px;">
                    ✓ <strong>Todas as {len(subs_disponiveis)} subprefeituras</strong> das zonas selecionadas estão ativas na análise.
                </div>
                """, unsafe_allow_html=True)
            else:
                subprefeituras_obs = st.multiselect(
                    "Selecione as subprefeituras específicas para análise:",
                    options=subs_disponiveis,
                    default=subs_disponiveis[:4] if len(subs_disponiveis) >= 4 else subs_disponiveis,
                    placeholder="Clique ou digite para buscar (ex: Sé, Itaquera, Capela do Socorro)..."
                )
                if not subprefeituras_obs:
                    subprefeituras_obs = subs_disponiveis

        st.markdown("---")
        st.markdown("##### 📊 2. Indicadores Socioeconômicos e Equipamentos:")
        f1, f2, f3 = st.columns(3)

        with f1:
            r_min = float(df_indicadores["renda_media_formal"].min())
            r_max = float(df_indicadores["renda_media_formal"].max())
            faixa_renda = st.slider(
                "Faixa de Renda Média Formal (R$):",
                min_value=r_min,
                max_value=r_max,
                value=(r_min, r_max),
                step=100.0,
                format="R$ %.0f"
            )

        with f2:
            d_min = float(df_indicadores["tempo_deslocamento_min"].min())
            d_max = float(df_indicadores["tempo_deslocamento_min"].max())
            faixa_desloc = st.slider(
                "Tempo de Deslocamento ao Trabalho (minutos):",
                min_value=d_min,
                max_value=d_max,
                value=(d_min, d_max),
                step=1.0,
                format="%.0f min"
            )

        with f3:
            idf_slider = st.slider(
                "Índice de Deserto de Fomento (IDF de 0.0 a 10.0):",
                min_value=0.0,
                max_value=10.0,
                value=(0.0, 10.0),
                step=0.1
            )
            filtro_equip = st.selectbox(
                "Presença de Equipamentos ADE SAMPA:",
                ["Todos os Distritos", "Apenas distritos COM equipamentos ativos", "Apenas distritos SEM equipamentos (vazio)"]
            )

    # Aplicação dos filtros do observatório
    if escopo_aplicacao == "Aplicar filtros aos gráficos selecionados":
        df_obs = df_indicadores[
            (df_indicadores["zona"].isin(zonas_obs)) &
            (df_indicadores["subprefeitura"].isin(subprefeituras_obs)) &
            (df_indicadores["classificacao_vulnerabilidade"].isin(classificacoes_obs)) &
            (df_indicadores["renda_media_formal"].between(faixa_renda[0], faixa_renda[1])) &
            (df_indicadores["tempo_deslocamento_min"].between(faixa_desloc[0], faixa_desloc[1])) &
            (df_indicadores["indice_deserto_fomento"].between(idf_slider[0], idf_slider[1]))
        ]
        if filtro_equip == "Apenas distritos COM equipamentos ativos":
            df_obs = df_obs[df_obs["equipamentos_adesampa_ativos"] > 0]
        elif filtro_equip == "Apenas distritos SEM equipamentos (vazio)":
            df_obs = df_obs[df_obs["equipamentos_adesampa_ativos"] == 0]
    else:
        df_obs = df_indicadores

    # Feedback de distritos filtrados
    if len(df_obs) == 0:
        st.warning("⚠️ Nenhum distrito corresponde aos filtros selecionados. Ajuste os intervalos nos filtros acima.")
    else:
        st.info(f"📊 Amostra ativa: **{len(df_obs)} de 96 distritos** ({len(df_obs)/96*100:.1f}% da cidade de São Paulo).")

    if not graficos_ativos:
        st.info("ℹ️ Nenhum gráfico selecionado para exibição. Abra o painel acima e marque quais gráficos deseja ver.")
    else:
        # Paleta consistente e amigável para regiões
        cores_zonas = {
            "Centro": "#10B981",
            "Oeste": "#06B6D4",
            "Norte": "#F59E0B",
            "Leste": "#EF4444",
            "Sul": "#8B5CF6"
        }

        # Configuração padrão de hoverlabel limpo e legível
        estilo_hoverlabel = dict(
            bgcolor="#FFFFFF",
            font_size=13,
            font_family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
            font_color="#0F172A",
            bordercolor="#CBD5E1"
        )

        # Grid dinâmico para renderizar os gráficos selecionados
        for nome_grafico in graficos_ativos:
            if nome_grafico == "Abismo Centro x Periferia (Dispersão: Renda vs Deslocamento)" and len(df_obs) > 0:
                st.markdown("##### 📍 Abismo Centro x Periferia (Renda vs Tempo de Deslocamento)")
                fig_disp = px.scatter(
                    df_obs,
                    x="tempo_deslocamento_min",
                    y="renda_media_formal",
                    color="zona",
                    size="populacao",
                    hover_name="distrito",
                    custom_data=["zona", "subprefeitura", "populacao", "indice_deserto_fomento", "equipamentos_adesampa_ativos"],
                    labels={
                        "tempo_deslocamento_min": "Tempo Médio até o Trabalho (minutos)",
                        "renda_media_formal": "Remuneração Média Formal (R$)",
                        "zona": "Região da Capital",
                        "populacao": "População"
                    },
                    title=f"Correlação: Deslocamento x Remuneração ({len(df_obs)} distritos)",
                    color_discrete_map=cores_zonas
                )
                fig_disp.update_traces(
                    hovertemplate=(
                        "<b>📍 Distrito: %{hovertext}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        "• <b>Região:</b> Zona %{customdata[0]}<br>"
                        "• <b>Subprefeitura:</b> %{customdata[1]}<br>"
                        "• <b>Tempo até o Trabalho:</b> %{x:.1f} minutos<br>"
                        "• <b>Renda Média Formal:</b> R$ %{y:,.2f}<br>"
                        "• <b>População Estimada:</b> %{customdata[2]:,.0f} habitantes<br>"
                        "• <b>Índice IDF (Deserto):</b> %{customdata[3]:.2f} de 10.0<br>"
                        "• <b>Equipamentos ADE SAMPA:</b> %{customdata[4]} ativos<br>"
                        "<extra></extra>"
                    )
                )
                fig_disp.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hoverlabel=estilo_hoverlabel
                )
                config_disp = obter_config_plotly_export("adesampa_abismo_centro_periferia")
                st.plotly_chart(fig_disp, use_container_width=True, config=config_disp)
                col_btn_disp, _ = st.columns([1.5, 2.5])
                with col_btn_disp:
                    st.download_button(
                        label="🖼️ Baixar Gráfico em Alta Resolução (PNG)",
                        data=lambda: exportar_figura_png(fig_disp),
                        file_name="adesampa_abismo_centro_periferia.png",
                        mime="image/png",
                        key="btn_dl_png_disp",
                        use_container_width=True,
                        help="Exporta a imagem PNG em alta resolução deste gráfico de dispersão."
                    )

            elif nome_grafico == "Top Desertos de Fomento (Ranking de Urgência IDF)" and len(df_obs) > 0:
                st.markdown("##### 🚨 Ranking de Distritos por Índice de Deserto de Fomento (IDF)")
                top_n = min(15, len(df_obs))
                ranking_obs = df_obs.sort_values(by="indice_deserto_fomento", ascending=False).head(top_n)
                fig_bar = px.bar(
                    ranking_obs,
                    x="indice_deserto_fomento",
                    y="distrito",
                    orientation="h",
                    color="zona",
                    labels={"indice_deserto_fomento": "Índice IDF (0 a 10)", "distrito": "Distrito"},
                    title=f"Top {top_n} Territórios com Maior Prioridade de Atendimento",
                    color_discrete_map=cores_zonas,
                    text=ranking_obs["indice_deserto_fomento"].apply(lambda v: f"{v:.2f}"),
                    custom_data=["zona", "subprefeitura", "renda_media_formal", "tempo_deslocamento_min", "equipamentos_adesampa_ativos"]
                )
                fig_bar.update_traces(
                    textposition="outside",
                    textfont=dict(size=12, color="#1E293B", family="-apple-system, sans-serif"),
                    hovertemplate=(
                        "<b>🚨 Distrito: %{y}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        "• <b>Índice IDF:</b> %{x:.2f} de 10.0 (Prioridade Alta)<br>"
                        "• <b>Região:</b> Zona %{customdata[0]}<br>"
                        "• <b>Subprefeitura:</b> %{customdata[1]}<br>"
                        "• <b>Renda Média Formal:</b> R$ %{customdata[2]:,.2f}<br>"
                        "• <b>Tempo de Deslocamento:</b> %{customdata[3]:.1f} minutos<br>"
                        "• <b>Equipamentos ADE SAMPA:</b> %{customdata[4]} ativos<br>"
                        "<extra></extra>"
                    )
                )
                fig_bar.update_layout(
                    yaxis=dict(autorange="reversed"),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hoverlabel=estilo_hoverlabel
                )
                config_bar = obter_config_plotly_export("adesampa_top_desertos_idf")
                st.plotly_chart(fig_bar, use_container_width=True, config=config_bar)
                col_btn_bar, _ = st.columns([1.5, 2.5])
                with col_btn_bar:
                    st.download_button(
                        label="🖼️ Baixar Gráfico em Alta Resolução (PNG)",
                        data=lambda: exportar_figura_png(fig_bar),
                        file_name="adesampa_top_desertos_idf.png",
                        mime="image/png",
                        key="btn_dl_png_bar",
                        use_container_width=True,
                        help="Exporta a imagem PNG em alta resolução deste ranking de desertos de fomento."
                    )

            elif nome_grafico == "Distribuição de Equipamentos por Zona (Teias, FabLabs e Postos)" and len(df_obs) > 0:
                st.markdown("##### 🏢 Presença Territorial de Equipamentos Públicos")
                equip_zona = df_obs.groupby("zona")["equipamentos_adesampa_ativos"].sum().reset_index()
                distritos_por_zona = df_obs.groupby("zona")["distrito"].count().to_dict()
                equip_zona["qtd_distritos"] = equip_zona["zona"].map(distritos_por_zona).fillna(0).astype(int)
                total_equip = int(equip_zona["equipamentos_adesampa_ativos"].sum())

                fig_pie = px.pie(
                    equip_zona,
                    names="zona",
                    values="equipamentos_adesampa_ativos",
                    title=f"Unidades ADE SAMPA por Região ({total_equip} unidades ativas)",
                    color="zona",
                    color_discrete_map=cores_zonas,
                    hole=0.4,
                    custom_data=["qtd_distritos"]
                )
                # Rótulos visíveis nas fatias e tooltip formatado em linguagem natural
                fig_pie.update_traces(
                    texttemplate="<b>Zona %{label}</b><br>%{value} un (%{percent})",
                    textposition="inside",
                    insidetextorientation="horizontal",
                    textfont=dict(size=13, color="#FFFFFF", family="-apple-system, BlinkMacSystemFont, sans-serif"),
                    hovertemplate=(
                        "<b>🏢 Região: Zona %{label}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        "• <b>Equipamentos ADE SAMPA:</b> %{value} unidades ativas<br>"
                        "• <b>Representatividade:</b> %{percent}<br>"
                        "• <b>Distritos nesta Região:</b> %{customdata[0]} distritos<br>"
                        f"• <b>Total na Amostra:</b> {total_equip} equipamentos<br>"
                        "<extra></extra>"
                    )
                )
                fig_pie.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hoverlabel=estilo_hoverlabel
                )
                config_pie = obter_config_plotly_export("adesampa_equipamentos_por_zona")
                st.plotly_chart(fig_pie, use_container_width=True, config=config_pie)
                col_btn_pie, _ = st.columns([1.5, 2.5])
                with col_btn_pie:
                    st.download_button(
                        label="🖼️ Baixar Gráfico em Alta Resolução (PNG)",
                        data=lambda: exportar_figura_png(fig_pie),
                        file_name="adesampa_equipamentos_por_zona.png",
                        mime="image/png",
                        key="btn_dl_png_pie",
                        use_container_width=True,
                        help="Exporta a imagem PNG em alta resolução da distribuição de equipamentos por região."
                    )

            elif nome_grafico == "Matriz de Vulnerabilidade Multidimensional (Renda x IDF x População)" and len(df_obs) > 0:
                st.markdown("##### 🎯 Matriz Multidimensional: Renda vs Índice de Deserto (IDF)")
                fig_bolhas = px.scatter(
                    df_obs,
                    x="renda_media_formal",
                    y="indice_deserto_fomento",
                    size="populacao",
                    color="classificacao_vulnerabilidade",
                    hover_name="distrito",
                    custom_data=["classificacao_vulnerabilidade", "zona", "subprefeitura", "populacao", "equipamentos_adesampa_ativos"],
                    labels={
                        "renda_media_formal": "Renda Média Formal (R$)",
                        "indice_deserto_fomento": "Índice IDF (0 a 10)",
                        "classificacao_vulnerabilidade": "Classificação",
                        "populacao": "População"
                    },
                    title="Vulnerabilidade Territorial Integrada",
                    color_discrete_map={
                        "Deserto Crítico (Prioridade 1)": "#DC2626",
                        "Deserto Moderado (Prioridade 2)": "#D97706",
                        "Em Cobertura (Prioridade 3)": "#0284C7",
                        "Polo Consolidado (Bem Assistido)": "#059669",
                        "Deserto Crítico": "#DC2626",
                        "Deserto Moderado": "#D97706",
                        "Em Cobertura": "#0284C7",
                        "Polo Consolidado": "#059669"
                    }
                )
                fig_bolhas.update_traces(
                    hovertemplate=(
                        "<b>🎯 Distrito: %{hovertext}</b><br>"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                        "• <b>Classificação:</b> %{customdata[0]}<br>"
                        "• <b>Região:</b> Zona %{customdata[1]} | Subprefeitura: %{customdata[2]}<br>"
                        "• <b>Renda Média Formal:</b> R$ %{x:,.2f}<br>"
                        "• <b>Índice IDF (Deserto):</b> %{y:.2f} de 10.0<br>"
                        "• <b>População Estimada:</b> %{customdata[3]:,.0f} habitantes<br>"
                        "• <b>Equipamentos ADE SAMPA:</b> %{customdata[4]} ativos<br>"
                        "<extra></extra>"
                    )
                )
                fig_bolhas.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hoverlabel=estilo_hoverlabel
                )
                config_bolhas = obter_config_plotly_export("adesampa_matriz_vulnerabilidade_multidimensional")
                st.plotly_chart(fig_bolhas, use_container_width=True, config=config_bolhas)
                col_btn_bolhas, _ = st.columns([1.5, 2.5])
                with col_btn_bolhas:
                    st.download_button(
                        label="🖼️ Baixar Gráfico em Alta Resolução (PNG)",
                        data=lambda: exportar_figura_png(fig_bolhas),
                        file_name="adesampa_matriz_vulnerabilidade.png",
                        mime="image/png",
                        key="btn_dl_png_bolhas",
                        use_container_width=True,
                        help="Exporta a imagem PNG em alta resolução da matriz multidimensional."
                    )

            elif nome_grafico == "Tabela Comparativa Agregada por Subprefeitura" and len(df_obs) > 0:
                st.markdown("##### 📋 Visão Sintética Agregada por Subprefeitura")
                resumo_sub = df_obs.groupby("subprefeitura").agg(
                    distritos_qtd=("distrito", "count"),
                    populacao_total=("populacao", "sum"),
                    renda_media=("renda_media_formal", "mean"),
                    deslocamento_medio=("tempo_deslocamento_min", "mean"),
                    equipamentos_total=("equipamentos_adesampa_ativos", "sum"),
                    idf_medio=("indice_deserto_fomento", "mean")
                ).reset_index().sort_values(by="idf_medio", ascending=False)

                st.dataframe(
                    resumo_sub.rename(columns={
                        "subprefeitura": "Subprefeitura",
                        "distritos_qtd": "Qtd Distritos",
                        "populacao_total": "População Total",
                        "renda_media": "Renda Média (R$)",
                        "deslocamento_medio": "Deslocamento Médio (min)",
                        "equipamentos_total": "Total Equipamentos",
                        "idf_medio": "IDF Médio"
                    }).style.format({
                        "População Total": "{:,.0f}",
                        "Renda Média (R$)": "R$ {:,.2f}",
                        "Deslocamento Médio (min)": "{:.1f}",
                        "IDF Médio": "{:.2f}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                csv_sub = resumo_sub.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    label="📥 Baixar Tabela por Subprefeitura (CSV)",
                    data=csv_sub,
                    file_name="adesampa_resumo_subprefeituras.csv",
                    mime="text/csv",
                    key="btn_dl_csv_subprefeitura",
                    help="Exporta o resumo de subprefeituras estruturado para Excel / CSV."
                )


# -------------------------------------------------------------
# ABA 4: CATÁLOGO DE EQUIPAMENTOS
# -------------------------------------------------------------
with aba_equipamentos:
    st.markdown("#### Unidades da Rede Teia, FabLabs Livres e Postos de Atendimento")
    st.caption("Relação oficial de endereços, infraestrutura de estúdios Sampa Cast e horários de funcionamento.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipo_filtro = st.multiselect(
            "Filtrar por Tipo:",
            ["Rede Teia", "FabLab Livre", "Posto de Atendimento"],
            default=["Rede Teia", "FabLab Livre", "Posto de Atendimento"]
        )
    with col_f2:
        apenas_cast = st.checkbox("Apenas unidades com Estúdio Sampa Cast 🎙️", value=False)

    equip_mostrados = [
        e for e in equipamentos
        if e.get("tipo") in tipo_filtro and (not apenas_cast or e.get("possui_sampa_cast"))
    ]

    for eq in equip_mostrados:
        sampa_tag = "🎙️ Possui Sampa Cast" if eq.get("possui_sampa_cast") else ""
        with st.expander(f"{eq['nome']} — {eq['distrito']} ({eq['zona']}) {sampa_tag}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"**Tipo:** {eq['tipo']} | **Categoria:** {eq['categoria']}")
                st.write(f"**Endereço:** {eq['endereco']}")
                st.write(f"**Horário:** {eq['horario']}")
            with c2:
                st.write("**Serviços Ofertados:**")
                for srv in eq.get("servicos", []):
                    st.write(f"• {srv}")


# -------------------------------------------------------------
# ABA 5: METODOLOGIA & SOBRE O EDITAL
# -------------------------------------------------------------
with aba_metodologia:
    st.markdown("""
    ### 🏛️ Sobre o Projeto e Cumprimento do Edital nº 005/2026
    
    Esta solução foi concebida sob medida para a **Prova Técnica Prática** do processo seletivo da **ADE SAMPA (Agência São Paulo de Desenvolvimento)**, cargo de **Assistente II - Dados e IA**.

    #### 1. Justificativa Pública do Tema
    A cidade de São Paulo possui um abismo socioeconômico histórico comprovado pelo *Mapa da Desigualdade*. Enquanto as oportunidades econômicas concentram-se no centro e no vetor sudoeste, as periferias concentram o empreendedorismo por sobrevivência e longos tempos de deslocamento diário. A **ADE SAMPA Territórios Inteligentes** permite que gestores públicos identifiquem onde alocar novas turmas da *Fábrica de Negócios*, novos coworkings públicos (*Rede Teia*) e mutirões de crédito (*CRED SAMPA*).

    #### 2. Metodologia do Índice de Deserto de Fomento (IDF)
    O **IDF** varia de `0.0` (atendido) a `10.0` (deserto crítico de fomento produtivo) e combina 4 dimensões oficiais:
    - **Vulnerabilidade de Renda (35%):** Relação entre a remuneração média do distrito e a referência da capital.
    - **Isolamento e Deslocamento (25%):** Penalidade proporcional para tempos médios de trânsito superiores a 45 minutos.
    - **Densidade Local de Empregos (20%):** Avaliação de postos de trabalho no próprio distrito (caracterização de bairro-dormitório).
    - **Ausência de Equipamentos Ativos (20%):** Penalidade para distritos sem postos da ADE SAMPA instalados.

    #### 3. Fontes de Dados Oficiais Utilizadas
    - 🌐 **[GeoSampa — Mapa Digital da Cidade de São Paulo](https://geosampa.prefeitura.sp.gov.br/)**: Malha cartográfica vetorial dos 96 distritos, divisões de subprefeituras e camadas territoriais municipais.
    - 📂 **[Portal de Dados Abertos da Cidade de São Paulo (PMSP)](https://dados.prefeitura.sp.gov.br/)**: Catálogo aberto da Prefeitura com relação oficial de endereços e coordenadas dos equipamentos públicos municipais.
    - 📊 **[Mapa da Desigualdade (Rede Nossa São Paulo / Instituto Cidades Sustentáveis)](https://www.nossasaopaulo.org.br/)**: Levantamento anual com indicadores distritais de remuneração média, tempo de deslocamento e postos de trabalho.
    - 🏛️ **[IBGE — Censo Demográfico e Estatísticas Territoriais](https://censo2022.ibge.gov.br/)**: Dados demográficos e contagem populacional consolidada por setor e distrito censitário.
    - 📈 **[Fundação SEADE — Sistema Estadual de Análise de Dados](https://repositorio.seade.gov.br/)**: Projeções demográficas, estatísticas socioeconômicas e repositório de dados abertos paulistas.
    - 🏢 **[Portal Oficial da ADE SAMPA](https://adesampa.com.br/)**: Programas de fomento, equipamentos públicos (Rede Teia, FabLabs Livres, Postos ADE SAMPA), capacitações e microcrédito orientado (CRED SAMPA).

    #### 4. Mapa do Site & Recursos de Apoio
    - 🗺️ **Guia do Usuário e Mapa do Site (`SITEMAP.md`)**: O repositório inclui um guia visual completo com roteiro de 5 minutos para a banca avaliadora, catálogo de todos os 7 gráficos e navegação tela a tela.
    - 🖼️ **Exportação Executiva Multi-Formato**: Suporte a download de gráficos em **PNG em alta resolução (300 DPI)**, tabelas em **CSV estruturado para Excel (`UTF-8 com BOM`)** e pareceres de IA em **Markdown**.
    - ♿ **Acessibilidade Digital (WCAG 2.1 AA)**: Todos os cartões de indicadores possuem marcadores semânticos e textos alternativos (*alt-text*) para leitura inclusiva e auditada.
    """)

    # Botão de download do PDF ilustrado na Aba 5
    pdf_path_aba5 = ROOT_DIR / "data" / "mapa_do_site_adesampa.pdf"
    if pdf_path_aba5.exists():
        with open(pdf_path_aba5, "rb") as f_pdf5:
            pdf_bytes_aba5 = f_pdf5.read()
        col_pdf_b, _ = st.columns([1.6, 2.4])
        with col_pdf_b:
            st.download_button(
                label="📄 Baixar Guia Visual & Mapa do Site (PDF Ilustrado)",
                data=pdf_bytes_aba5,
                file_name="mapa_do_site_adesampa.pdf",
                mime="application/pdf",
                key="dl_btn_sitemap_pdf_aba5",
                use_container_width=True,
                help="Download do documento PDF oficial com capturas de tela e roteiro completo."
            )
