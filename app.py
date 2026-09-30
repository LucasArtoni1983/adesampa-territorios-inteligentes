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


def detectar_ambiente() -> str:
    """Detecta dinamicamente se o app está rodando na nuvem (Streamlit Community Cloud) ou em máquina local."""
    import os
    caminho = Path(__file__).resolve().as_posix()
    if "/mount/src" in caminho or "/app" in caminho or os.getenv("STREAMLIT_SHARING_HOST") or (os.name != "nt" and os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"):
        return "Nuvem (Streamlit Cloud)"
    return "Execução Local"


# 1. Configuração da Página
st.set_page_config(
    page_title="ADE SAMPA Territórios Inteligentes",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS de Engenharia Cívica & Observatório Territorial (Human-Crafted GovTech & WCAG 2.1 AA)
st.markdown("""
<style>
    /* Tipografia Moderna e Numérica Editorial: Plus Jakarta Sans & Inter */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, [data-testid="stSidebar"], button, input, select, textarea {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Padrão Numérico de Precisão Estatística (Tabular Numerals / SEADE / IBGE / GDS) */
    .tabular-nums, .kpi-value, [data-testid="stMetricValue"] {
        font-variant-numeric: tabular-nums lining-nums !important;
        font-feature-settings: "tnum" 1, "lnum" 1, "cv02" 1, "cv03" 1, "cv04" 1 !important;
    }

    /* WCAG 2.4.1: Atalho de Pular Navegação (Skip Link 100% invisível até receber foco) */
    .skip-link {
        position: fixed !important;
        top: 20px !important;
        left: 50% !important;
        transform: translate(-50%, -200%) !important;
        opacity: 0 !important;
        pointer-events: none !important;
        background: #0B192C !important;
        color: #FFFFFF !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        z-index: 9999999 !important;
        text-decoration: none !important;
        border: 2px solid #38BDF8 !important;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.4) !important;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease !important;
    }
    .skip-link:focus, .skip-link:focus-visible {
        transform: translate(-50%, 0) !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        outline: 3px solid #38BDF8 !important;
        outline-offset: 3px !important;
    }

    /* WCAG 2.4.7: Foco Visível com Anel Duplo de Alto Contraste */
    :focus-visible, 
    button:focus-visible, 
    [tabindex]:focus-visible, 
    input:focus-visible, 
    select:focus-visible, 
    [data-baseweb="tab"]:focus-visible,
    div[data-testid="stCheckbox"] input:focus-visible {
        outline: 2px solid #FFFFFF !important;
        box-shadow: 0 0 0 4px #003399 !important;
        outline-offset: 1px !important;
    }

    /* WCAG 2.3.3: Preferência de Movimento Reduzido */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
        .pulse-dot {
            animation: none !important;
        }
        .kpi-card:hover, .metric-card:hover {
            transform: none !important;
        }
    }

    /* Ambiência Cartográfica Sóbria e Estruturada */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: 
            linear-gradient(rgba(15, 23, 42, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15, 23, 42, 0.02) 1px, transparent 1px) !important;
        background-size: 32px 32px !important;
    }

    /* ========================================================
       CABEÇALHO INSTITUCIONAL PMSP / ADE SAMPA (GRID CADASTRAL)
       ======================================================== */
    .main-header {
        background: #0B192C;
        background-image: 
            radial-gradient(at 100% 0%, rgba(30, 58, 138, 0.45) 0px, transparent 65%),
            linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
        background-size: 100% 100%, 24px 24px, 24px 24px;
        padding: 22px 28px 20px 28px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 18px;
        border: 1px solid #1E293B;
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.18), 0 2px 6px rgba(15, 23, 42, 0.06);
    }
    .gov-topbar {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94A3B8;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    }
    .gov-seal-pill {
        background: #1E293B;
        border: 1px solid #334155;
        color: #F8FAFC;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 9.5px;
        font-weight: 800;
        letter-spacing: 0.08em;
    }
    .header-content {
        display: flex;
        align-items: center;
        gap: 22px;
    }
    .header-logo-container {
        width: 76px;
        height: 76px;
        border-radius: 12px;
        background: #FFFFFF;
        padding: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .header-logo {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .header-meta-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
    }
    .meta-tag {
        font-size: 10.5px;
        font-weight: 700;
        padding: 2.5px 8px;
        border-radius: 4px;
        letter-spacing: 0.04em;
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(15, 23, 42, 0.65);
        color: #E2E8F0;
    }
    .meta-tag.tag-a11y {
        background: #064E3B;
        border-color: #059669;
        color: #D1FAE5;
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 24px !important;
        margin: 0 !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        line-height: 1.25 !important;
    }
    .main-header p {
        color: #CBD5E1 !important;
        font-size: 13.5px !important;
        margin: 4px 0 0 0 !important;
        line-height: 1.45 !important;
        max-width: 860px;
    }

    /* ========================================================
       BIGNUMBERS COM BENCHMARKS CONTEXTUAIS (EDWARD TUFTE)
       ======================================================== */
    .kpi-card {
        background: #FFFFFF;
        padding: 14px 16px 14px 16px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        min-height: 156px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .kpi-card:hover {
        border-color: #64748B;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.07);
    }
    .kpi-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2px;
    }
    .kpi-source-tag {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
        background: #F1F5F9;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #E2E8F0;
        display: inline-block;
    }
    .kpi-source-meaning {
        font-size: 9.5px;
        color: #64748B;
        font-weight: 600;
        line-height: 1.25;
        margin-top: 2px;
        margin-bottom: 2px;
        letter-spacing: -0.01em;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    abbr[title], .sigla-abbr {
        text-decoration: underline dotted #94A3B8;
        text-underline-offset: 2.5px;
        cursor: help;
    }
    .siglas-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px 16px;
        font-size: 12px;
        color: #334155;
        line-height: 1.45;
        padding: 6px 0;
    }
    @media (max-width: 768px) {
        .siglas-grid {
            grid-template-columns: 1fr;
        }
    }
    .kpi-indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1.25;
        margin-top: 4px;
    }
    .kpi-num-row {
        display: flex;
        align-items: baseline;
        gap: 5px;
        margin: 4px 0 6px 0;
    }
    .kpi-value {
        font-size: 1.52rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        letter-spacing: -0.03em;
        font-variant-numeric: tabular-nums lining-nums;
        font-feature-settings: "tnum" 1, "lnum" 1;
    }
    .kpi-unit {
        font-size: 0.8rem;
        font-weight: 700;
        color: #475569;
    }
    .kpi-benchmark-bar {
        width: 100%;
        height: 3px;
        background: #F1F5F9;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 6px;
    }
    .kpi-benchmark-fill {
        height: 100%;
        border-radius: 2px;
    }
    .kpi-context-row {
        font-size: 0.73rem;
        color: #334155;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
        line-height: 1.3;
    }

    /* ========================================================
       NAVEGAÇÃO POR ABAS TIPO TERMINAL CÍVICO
       ======================================================== */
    div[data-baseweb="tab-list"] {
        background: #F1F5F9 !important;
        padding: 4px !important;
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        gap: 4px !important;
        margin-bottom: 20px !important;
        display: flex !important;
        width: fit-content !important;
        max-width: 100% !important;
    }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {
        border: none !important;
        border-radius: 7px !important;
        background: transparent !important;
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        padding: 9px 16px !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
    }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"]:hover {
        background: #E2E8F0 !important;
        color: #0F172A !important;
    }
    div[data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: #003399 !important;
        font-weight: 800 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1) !important;
        border: 1px solid #CBD5E1 !important;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ========================================================
       BARRA LATERAL DE GOVERNANÇA TERRITORIAL
       ======================================================== */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #CBD5E1 !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 16px 0 !important;
        border-color: #CBD5E1 !important;
    }
    .sidebar-brand-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }
    .sidebar-logo-img {
        width: 130px;
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        background: #FFFFFF;
        display: block;
        margin: 0 auto;
    }
    .sidebar-section-title {
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #1E293B;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sidebar-status-box {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        font-size: 0.8rem;
        line-height: 1.5;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 5px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Cards e Elementos Auxiliares */
    .metric-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #003399;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }
    .metric-card h4 {
        color: #003399;
        margin: 0 0 10px 0;
        font-size: 16.5px;
        font-weight: 800;
    }
    .badge-critico {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 9px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }
    .badge-moderado {
        background-color: #FFFBEB;
        color: #854D0E;
        border: 1px solid #FDE68A;
        padding: 3px 9px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }
    .badge-atendido {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 3px 9px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }
    .badge-consolidado {
        background-color: #F0F9FF;
        color: #075985;
        border: 1px solid #BAE6FD;
        padding: 3px 9px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }

    /* Botões Padrão GovTech */
    div.stButton > button, div.stDownloadButton > button {
        min-height: 44px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button[kind="primary"] {
        background: #003399 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 51, 153, 0.25) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #002266 !important;
        box-shadow: 0 4px 8px rgba(0, 51, 153, 0.35) !important;
    }
    div.stButton > button[kind="secondary"], div.stDownloadButton > button {
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    }
    div.stButton > button[kind="secondary"]:hover, div.stDownloadButton > button:hover {
        background: #F1F5F9 !important;
        border-color: #64748B !important;
        color: #0F172A !important;
    }

    /* Tabelas e Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }

    /* ========================================================
       COMPONENTES DE DESIGN CÍVICO & CARTOGRAFIA INSTITUCIONAL
       ======================================================== */
    .civic-legend-box {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .legend-header {
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .legend-header-kicker {
        display: block;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #64748B;
    }
    .legend-header-title {
        font-size: 13.5px;
        font-weight: 800;
        color: #0F172A;
    }
    .legend-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
    }
    .legend-item {
        border-radius: 8px;
        padding: 10px 12px;
        border: 1px solid #E2E8F0;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }
    .legend-badge-row {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11.5px;
        font-weight: 800;
    }
    .legend-swatch {
        width: 10px;
        height: 10px;
        border-radius: 2px;
        display: inline-block;
        flex-shrink: 0;
    }
    .legend-desc {
        font-size: 11px;
        color: #475569;
        line-height: 1.35;
    }

    /* Ficha Cadastral do Distrito (Aba 2) */
    .ficha-cadastral {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        margin-bottom: 14px;
    }
    .ficha-kicker {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #003399;
        margin-bottom: 4px;
    }
    .ficha-title {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    .ficha-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 14px;
    }
    .ficha-pill {
        font-size: 11px;
        font-weight: 700;
        padding: 2.5px 8px;
        border-radius: 4px;
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
    }
    .ficha-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        padding: 12px 0;
        border-top: 1px solid #F1F5F9;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 12px;
    }
    .ficha-stat-label {
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.04em;
    }
    .ficha-stat-val {
        font-size: 15px;
        font-weight: 800;
        color: #0F172A;
        font-variant-numeric: tabular-nums lining-nums;
    }

    /* Barra de Síntese de Equipamentos (Aba 4) */
    .equip-summary-bar {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 16px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .equip-stat-item {
        display: flex;
        align-items: baseline;
        gap: 6px;
    }
    .equip-stat-num {
        font-size: 18px;
        font-weight: 800;
        color: #0F172A;
        font-variant-numeric: tabular-nums lining-nums;
    }
    .equip-stat-txt {
        font-size: 12px;
        font-weight: 600;
        color: #475569;
    }
    .service-chip {
        display: inline-block;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        color: #334155;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        margin: 2px 4px 2px 0;
    }

    /* Cards Metodológicos do IDF (Aba 5) */
    .method-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 14px 0 20px 0;
    }
    .method-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        border-top: 3px solid #003399;
    }
    .method-card-pct {
        font-size: 18px;
        font-weight: 800;
        color: #003399;
        font-variant-numeric: tabular-nums lining-nums;
        margin-bottom: 4px;
    }
    .method-card-title {
        font-size: 12px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .method-card-desc {
        font-size: 11px;
        color: #475569;
        line-height: 1.4;
    }

    /* Rodapé Institucional do Observatório Municipal */
    .civic-footer {
        margin-top: 45px;
        background: #0B192C;
        border-radius: 12px;
        padding: 24px 28px;
        color: #94A3B8;
        border: 1px solid #1E293B;
        font-size: 12px;
        line-height: 1.5;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.15);
    }
    .civic-footer-inner {
        display: grid;
        grid-template-columns: 1.2fr 1.2fr 1fr;
        gap: 24px;
    }
    .civic-footer-col {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .footer-title {
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .footer-sub {
        font-size: 11.5px;
        color: #CBD5E1;
    }
    .footer-meta {
        font-size: 10.5px;
        color: #64748B;
        margin-top: 4px;
    }
</style>

<!-- WCAG 2.4.1: Atalho de Teclado para Pular para o Conteúdo Principal -->
<a href="#conteudo-principal" class="skip-link">Pular para o conteúdo principal (Atalho de Acessibilidade)</a>
""", unsafe_allow_html=True)


# 2. Carregamento dos Dados
df_indicadores = carregar_indicadores()
equipamentos = carregar_equipamentos()
geojson_distritos = carregar_geojson_distritos()
metricas_cidade = obter_metricas_gerais(df_indicadores, equipamentos)


# 3. Barra Lateral (Filtros e Controles)
with st.sidebar:
    # Logotipo oficial da ADE SAMPA em card institucional com suporte a acessibilidade
    logo_sidebar_b64 = carregar_logo_base64(str(LOGO_PATH))
    if logo_sidebar_b64:
        st.markdown(
            f"""
            <div class="sidebar-brand-card" role="region" aria-label="Identificação Institucional ADE SAMPA">
                <img src="data:image/png;base64,{logo_sidebar_b64}" 
                     class="sidebar-logo-img" 
                     alt="Logotipo Oficial da ADE SAMPA - Agência São Paulo de Desenvolvimento" />
                <div style="font-size: 11px; font-weight: 800; color: #003399; margin-top: 8px; letter-spacing: 0.06em;">
                    PREFEITURA DE SÃO PAULO
                </div>
                <div style="font-size: 10px; color: #334155; font-weight: 600; letter-spacing: 0.03em;">
                    ADE SAMPA • Observatório Territorial
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.image("https://adesampa.com.br/wp-content/themes/adesampa/assets/images/logo.png", use_container_width=True)

    st.markdown('<div class="sidebar-section-title">Parâmetros Territoriais</div>', unsafe_allow_html=True)

    # Filtro por Zona
    zonas_disponiveis = ["Todas"] + sorted(list(df_indicadores["zona"].unique()))
    zona_sel = st.selectbox("Zona da Capital:", zonas_disponiveis, help="Filtre os distritos pela macrorregião geográfica da cidade de São Paulo.")

    # Filtro por Subprefeitura
    if zona_sel != "Todas":
        sub_filtradas = sorted(list(df_indicadores[df_indicadores["zona"] == zona_sel]["subprefeitura"].unique()))
    else:
        sub_filtradas = sorted(list(df_indicadores["subprefeitura"].unique()))
    sub_sel = st.selectbox("Subprefeitura:", ["Todas"] + sub_filtradas, help="Filtre pela subprefeitura administrativa responsável.")

    # Filtro de desertos
    apenas_desertos = st.checkbox("Apenas Desertos de Fomento (IDF ≥ 5.5)", value=False, help="Restringe a visualização a distritos prioritários com índice de deserto moderado ou crítico.")

    # Busca textual
    busca_nome = st.text_input("Buscar distrito:", placeholder="Ex: Brasilândia, Grajaú...", help="Digite parte do nome de qualquer um dos 96 distritos paulistanos.")

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
    st.markdown('<div class="sidebar-section-title">Exportação Cadastral</div>', unsafe_allow_html=True)
    st.download_button(
        label=f"Baixar Base Filtrada ({len(df_filtrado)} distritos)",
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
            label="Baixar Mapa do Site (PDF)",
            data=pdf_bytes_side,
            file_name="mapa_do_site_adesampa.pdf",
            mime="application/pdf",
            key="dl_btn_sitemap_pdf_sidebar",
            use_container_width=True,
            help="Guia completo com capturas de tela fidedignas, catálogo dos 7 gráficos e roteiro de avaliação em 5 minutos para a banca."
        )

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">Parâmetros Cartográficos</div>', unsafe_allow_html=True)
    mostrar_raio = st.checkbox("Exibir Raios de Cobertura (2.5 km)", value=True, help="Raio de atendimento estimado de cada Teia e FabLab")

    st.markdown("---")
    # Painel de Status de Conexão e Metadados do Sistema (WCAG 4.1.2: aria-live)
    status_online = verificar_conexao_externa()
    if status_online:
        badge_cor = "#065F46"
        badge_bg = "#ECFDF5"
        badge_border = "#6EE7B7"
        status_texto = "Conectado"
        dot_cor = "#10B981"
        status_subtexto = "Rede externa operacional"
    else:
        badge_cor = "#991B1B"
        badge_bg = "#FEF2F2"
        badge_border = "#FCA5A5"
        status_texto = "Offline"
        dot_cor = "#EF4444"
        status_subtexto = "Modo de contingência local"

    st.markdown(f"""
    <div class="sidebar-status-box" role="status" aria-live="polite">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 800; color: #0F172A; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.05em;">Status do Sistema</span>
            <span style="background-color: {badge_bg}; color: {badge_cor}; border: 1px solid {badge_border}; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; display: inline-flex; align-items: center; gap: 5px;">
                <span class="pulse-dot" style="background-color: {dot_cor};"></span>
                {status_texto}
            </span>
        </div>
        <div style="font-size: 0.74rem; color: #334155; margin-bottom: 8px; font-weight: 500;">{status_subtexto}</div>
        <div style="font-size: 0.75rem; color: #334155; display: grid; gap: 3px; border-top: 1px solid #E2E8F0; padding-top: 6px;">
            <div><strong>Ambiente:</strong> {detectar_ambiente()}</div>
            <div><strong>Versão:</strong> v1.0.0 (Estável)</div>
            <div><strong>Bases:</strong> GeoSampa • PMSP • SEADE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Recarregar Dados", use_container_width=True, help="Limpa o cache em memória e recarrega as bases do disco"):
        st.cache_data.clear()
        st.rerun()


# 4. Cabeçalho Principal (com Logotipo Oficial no canto superior esquerdo e Semântica de Banner WCAG)
logo_b64 = carregar_logo_base64(str(LOGO_PATH))
img_tag = f'<div class="header-logo-container"><img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="Logotipo Oficial ADE SAMPA" /></div>' if logo_b64 else ''

st.markdown(f"""
<header class="main-header" role="banner" aria-label="Observatório de Inteligência Territorial ADE SAMPA">
    <div class="gov-topbar">
        <span class="gov-seal-pill">PMSP</span>
        <span>PREFEITURA DA CIDADE DE SÃO PAULO</span>
        <span>•</span>
        <span>DESENVOLVIMENTO ECONÔMICO E TRABALHO</span>
        <span>•</span>
        <span>ADE SAMPA</span>
    </div>
    <div class="header-content">
        {img_tag}
        <div style="flex-grow: 1;">
            <div class="header-meta-row">
                <span class="meta-tag">Edital nº 005/2026</span>
                <span class="meta-tag">GeoSampa • SIRGAS 2000</span>
                <span class="meta-tag tag-a11y">♿ Padrão WCAG 2.1 AA</span>
                <span class="meta-tag">96 Distritos Paulistanos</span>
            </div>
            <h1>ADE SAMPA • Territórios Inteligentes</h1>
            <p>Diagnóstico Geoespacial de Vulnerabilidade, Mobilidade e Cobertura de Equipamentos Públicos de Fomento</p>
        </div>
    </div>
</header>
""", unsafe_allow_html=True)


# 5. Métricas Resumo no Topo (Design de Observatório Cívico com Benchmarks Contextuais de SP)
col1, col2, col3, col4, col5 = st.columns(5)

kpi_data = [
    {
        "fonte_sigla": "SEADE / CENSO 2022",
        "fonte_extenso": "Fundação SEADE & Censo Demográfico IBGE",
        "fonte_tooltip": "SEADE: Fundação Sistema Estadual de Análise de Dados | CENSO: Censo Demográfico do IBGE",
        "label": "População Residente",
        "value": f"{metricas_cidade['populacao_total']:,}".replace(",", "."),
        "unidade": "hab",
        "contexto": "100% da capital • 96 distritos",
        "aria_label": f"População total de {metricas_cidade['populacao_total']} habitantes distribuídos nos 96 distritos de São Paulo. Fonte: Fundação SEADE e Censo Demográfico do IBGE",
        "title": "Estimativa populacional consolidada: SEADE (Fundação Sistema Estadual de Análise de Dados) e Censo IBGE",
        "accent": "#003399",
        "fill_width": "100%"
    },
    {
        "fonte_sigla": "RAIS / CAGED 2024",
        "fonte_extenso": "Rel. Anual de Informações Sociais & Caged",
        "fonte_tooltip": "RAIS: Relação Anual de Informações Sociais | CAGED: Cadastro Geral de Empregados e Desempregados (MTE)",
        "label": "Renda Média Formal",
        "value": f"R$ {metricas_cidade['renda_media_cidade']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "unidade": "",
        "contexto": "Disparidade territorial: até 4,8x",
        "aria_label": f"Renda média formal de R$ {metricas_cidade['renda_media_cidade']:.2f} na capital paulista. Fonte: RAIS e CAGED do Ministério do Trabalho",
        "title": "Remuneração média formal calculada via RAIS (Relação Anual de Informações Sociais) e CAGED",
        "accent": "#0F766E",
        "fill_width": "62%"
    },
    {
        "fonte_sigla": "PESQUISA OD METRÔ",
        "fonte_extenso": "Pesquisa Origem e Destino do Metrô SP",
        "fonte_tooltip": "OD: Pesquisa Origem e Destino da Companhia do Metropolitano de São Paulo",
        "label": "Tempo de Deslocamento",
        "value": f"{metricas_cidade['tempo_medio_deslocamento']}",
        "unidade": "min",
        "contexto": "Casa-trabalho • Meta: <30 min",
        "aria_label": f"Tempo médio de deslocamento de {metricas_cidade['tempo_medio_deslocamento']} minutos até o local de trabalho. Fonte: Pesquisa Origem e Destino (OD) do Metrô",
        "title": "Tempo médio diário de deslocamento casa-trabalho medido pela Pesquisa Origem e Destino (OD) do Metrô de São Paulo",
        "accent": "#0284C7",
        "fill_width": "78%"
    },
    {
        "fonte_sigla": "REDE MUNICIPAL",
        "fonte_extenso": "Equipamentos Públicos PMSP & ADE SAMPA",
        "fonte_tooltip": "PMSP: Prefeitura do Município de São Paulo | ADE SAMPA: Agência São Paulo de Desenvolvimento",
        "label": "Equipamentos Ativos",
        "value": f"{metricas_cidade['total_equipamentos']}",
        "unidade": "unidades",
        "contexto": "Teias, FabLabs e Postos • 33 Subp.",
        "aria_label": f"{metricas_cidade['total_equipamentos']} unidades ativas de fomento da ADE SAMPA (Agência São Paulo de Desenvolvimento)",
        "title": "Rede de coworkings Teia, FabLabs Livres e postos de atendimento da ADE SAMPA nas subprefeituras",
        "accent": "#5B21B6",
        "fill_width": "45%"
    },
    {
        "fonte_sigla": "MATRIZ TERRITORIAL IDF",
        "fonte_extenso": "Índice de Deserto de Fomento (ADE SAMPA)",
        "fonte_tooltip": "IDF: Índice de Deserto de Fomento (indicador de carência territorial de 0 a 10)",
        "label": "Desertos Críticos",
        "value": f"{metricas_cidade['desertos_criticos_qtd']}",
        "unidade": "distritos",
        "contexto": "IDF ≥ 7,5 • Prioridade Edital",
        "aria_label": f"{metricas_cidade['desertos_criticos_qtd']} distritos classificados como desertos críticos com Índice de Deserto de Fomento (IDF) maior ou igual a 7.5",
        "title": "Territórios periféricos com alta carência avaliada pelo IDF (Índice de Deserto de Fomento da ADE SAMPA)",
        "accent": "#991B1B",
        "fill_width": "85%"
    }
]

for col, kpi in zip([col1, col2, col3, col4, col5], kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" 
             role="region"
             aria-roledescription="indicador analítico municipal"
             aria-label="{kpi['aria_label']}" 
             title="{kpi['title']}">
            <div class="kpi-card-top">
                <abbr class="kpi-source-tag" title="{kpi['fonte_tooltip']}" tabindex="0">{kpi['fonte_sigla']}</abbr>
                <span class="kpi-indicator-dot" style="background-color: {kpi['accent']};" aria-hidden="true"></span>
            </div>
            <div class="kpi-source-meaning" title="{kpi['fonte_tooltip']}">{kpi['fonte_extenso']}</div>
            <div class="kpi-label">{kpi['label']}</div>
            <div class="kpi-num-row">
                <span class="kpi-value">{kpi['value']}</span>
                <span class="kpi-unit">{kpi['unidade']}</span>
            </div>
            <div class="kpi-benchmark-bar" aria-hidden="true">
                <div class="kpi-benchmark-fill" style="width: {kpi['fill_width']}; background-color: {kpi['accent']};"></div>
            </div>
            <div class="kpi-context-row">
                <span>{kpi['contexto']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Guia Rápido de Siglas e Fontes Oficiais (Acessível e Imediato)
with st.expander("📖 Guia de Siglas & Fontes Oficiais (Clique para ver o significado de cada sigla)", expanded=False):
    st.markdown("""<div class="siglas-grid">
<div><strong>• ADE SAMPA:</strong> Agência São Paulo de Desenvolvimento (PMSP / SMDET).</div>
<div><strong>• IDF:</strong> Índice de Deserto de Fomento (0.0 a 10.0 — mede a carência territorial de apoio ao empreendedor).</div>
<div><strong>• SEADE:</strong> Fundação Sistema Estadual de Análise de Dados (órgão paulista de estatísticas socioeconômicas).</div>
<div><strong>• CENSO / IBGE:</strong> Censo Demográfico do Instituto Brasileiro de Geografia e Estatística.</div>
<div><strong>• RAIS:</strong> Relação Anual de Informações Sociais (registro de empregos e remunerações formais — MTE).</div>
<div><strong>• CAGED:</strong> Cadastro Geral de Empregados e Desempregados (fluxo mensal de contratações CLT).</div>
<div><strong>• OD METRÔ:</strong> Pesquisa Origem e Destino do Metrô de São Paulo (padrões de mobilidade e deslocamento).</div>
<div><strong>• PMSP / SMDET:</strong> Prefeitura de São Paulo / Secretaria Municipal de Desenvolvimento Econômico e Trabalho.</div>
<div><strong>• SIRGAS 2000:</strong> Sistema de Referência Geocêntrico para as Américas (datum cartográfico oficial do GeoSampa).</div>
<div><strong>• WCAG 2.1 AA:</strong> Web Content Accessibility Guidelines (padrão internacional de acessibilidade digital).</div>
<div><strong>• MEI:</strong> Microempreendedor Individual (modelo de formalização simplificada para pequenos negócios).</div>
<div><strong>• Subp. / Subpref.:</strong> Subprefeituras Administrativas da Cidade de São Paulo (32 circunscrições).</div>
</div>""", unsafe_allow_html=True)


# Âncora de destino do Skip Link para navegação acessível por teclado
st.markdown('<div id="conteudo-principal" tabindex="-1" style="outline: none; margin-top: 8px;"></div>', unsafe_allow_html=True)


# 6. Navegação em Abas Principais (Padrão Observatório Governamental)
aba_mapa, aba_ia, aba_graficos, aba_equipamentos, aba_metodologia = st.tabs([
    "01 • Cartografia Territorial",
    "02 • Copiloto Analítico & IA",
    "03 • Observatório de Disparidades",
    "04 • Rede de Equipamentos Públicos",
    "05 • Metodologia & Documentação"
])


# -------------------------------------------------------------
# ABA 1: MAPA TERRITORIAL
# -------------------------------------------------------------
with aba_mapa:
    st.markdown("#### Distribuição Territorial e Pontos Cegos de Cobertura")
    st.caption("Passe o cursor sobre os distritos para visualizar indicadores. Cores mais quentes (vermelho/laranja) indicam maior urgência de novos investimentos.")

    # Legenda Oficial PMSP / ADE SAMPA: Vulnerabilidade Territorial e Equipamentos Públicos
    st.markdown("""<div class="civic-legend-box" role="region" aria-label="Convenção Cartográfica e Legenda Oficial">
<div class="legend-header">
<span class="legend-header-kicker">CONVENÇÃO CARTOGRÁFICA OFICIAL • GEOSAMPA / SIRGAS 2000</span>
<span class="legend-header-title">Índice de Deserto de Fomento (IDF) & Equipamentos Municipais</span>
</div>
<div style="font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
Grau de Vulnerabilidade Territorial (Gradiente Coroplético IDF):
</div>
<div class="legend-grid-4">
<div class="legend-item" style="background: #FEF2F2; border-color: #FECACA;">
<div class="legend-badge-row" style="color: #991B1B;"><span class="legend-swatch" style="background-color: #DC2626;"></span>Deserto Crítico (IDF ≥ 7.5)</div>
<div class="legend-desc">Carência severa de fomento, renda vulnerável e longo deslocamento.</div>
</div>
<div class="legend-item" style="background: #FFFBEB; border-color: #FDE68A;">
<div class="legend-badge-row" style="color: #92400E;"><span class="legend-swatch" style="background-color: #D97706;"></span>Deserto Moderado (5.5 a 7.4)</div>
<div class="legend-desc">Território em transição; prioridade para expansão de programas.</div>
</div>
<div class="legend-item" style="background: #EFF6FF; border-color: #BFDBFE;">
<div class="legend-badge-row" style="color: #1E40AF;"><span class="legend-swatch" style="background-color: #2563EB;"></span>Em Cobertura (3.5 a 5.4)</div>
<div class="legend-desc">Atendimento sob monitoramento regular e alcance satisfatório.</div>
</div>
<div class="legend-item" style="background: #ECFDF5; border-color: #A7F3D0;">
<div class="legend-badge-row" style="color: #065F46;"><span class="legend-swatch" style="background-color: #059669;"></span>Polo Consolidado (&lt; 3.5)</div>
<div class="legend-desc">Território estruturado, alta densidade econômica e de serviços.</div>
</div>
</div>
<div style="font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 14px; margin-bottom: 8px;">
Tipologia da Rede Municipal de Fomento ao Empreendedorismo:
</div>
<div class="legend-grid-4">
<div class="legend-item" style="background: #FFFFFF; border-top: 3px solid #2563EB;">
<div class="legend-badge-row" style="color: #1D4ED8;"><span class="legend-swatch" style="background-color: #2563EB;"></span>Rede Teia</div>
<div class="legend-desc">Coworking público gratuito com internet de alta velocidade, computadores e cursos.</div>
</div>
<div class="legend-item" style="background: #FFFFFF; border-top: 3px solid #7C3AED;">
<div class="legend-badge-row" style="color: #6D28D9;"><span class="legend-swatch" style="background-color: #7C3AED;"></span>FabLab Livre SP</div>
<div class="legend-desc">Laboratório de fabricação digital, impressoras 3D, cortadoras a laser e prototipagem.</div>
</div>
<div class="legend-item" style="background: #FFFFFF; border-top: 3px solid #EA580C;">
<div class="legend-badge-row" style="color: #C2410C;"><span class="legend-swatch" style="background-color: #EA580C;"></span>Posto ADE SAMPA</div>
<div class="legend-desc">Atendimento presencial, regularização MEI, capacitações e microcrédito Cred Sampa.</div>
</div>
<div class="legend-item" style="background: #FFFFFF; border-top: 3px solid #0284C7;">
<div class="legend-badge-row" style="color: #0284C7;"><span class="legend-swatch" style="background-color: #0284C7;"></span>Raio de Cobertura (2.5 km)</div>
<div class="legend-desc">Área de influência direta estimada de atendimento por mobilidade ativa ou local.</div>
</div>
</div>
<div style="font-size: 11px; color: #64748B; margin-top: 10px; display: flex; align-items: center; gap: 6px;">
<span style="font-weight: 800; color: #0F172A;">ESTÚDIOS SAMPA CAST:</span> Unidades selecionadas contam com cabine de isolamento acústico e equipamentos para produção de podcasts e mídias digitais.
</div>
</div>""", unsafe_allow_html=True)

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
    st.markdown("#### Pareceres Técnicos & Diagnóstico Territorial com IA")
    st.caption("Gere pareceres técnicos fundamentados para qualquer um dos 96 distritos paulistanos, identificando déficits de cobertura e propondo ações prioritárias da ADE SAMPA.")

    col_sel_distrito, col_info_rapida = st.columns([1, 2])

    with col_sel_distrito:
        distritos_ordenados = sorted(list(df_indicadores["distrito"].unique()))
        # Sugestão padrão em distrito crítico periférico
        idx_padrao = distritos_ordenados.index("Brasilândia") if "Brasilândia" in distritos_ordenados else 0
        distrito_escolhido = st.selectbox("Selecione o Distrito para Análise:", distritos_ordenados, index=idx_padrao)

        dados_distrito = df_indicadores[df_indicadores["distrito"] == distrito_escolhido].iloc[0].to_dict()
        equipamentos_locais = buscar_equipamentos_por_distrito(equipamentos, distrito_escolhido)

        idf_dist = float(dados_distrito['indice_deserto_fomento'])
        if idf_dist >= 7.5:
            badge_idf = '<span style="background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px;">Deserto Crítico (IDF ≥ 7.5)</span>'
        elif idf_dist >= 5.5:
            badge_idf = '<span style="background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px;">Deserto Moderado (IDF 5.5 - 7.4)</span>'
        elif idf_dist >= 3.5:
            badge_idf = '<span style="background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px;">Em Cobertura (IDF 3.5 - 5.4)</span>'
        else:
            badge_idf = '<span style="background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px;">Polo Consolidado (IDF &lt; 3.5)</span>'

        st.markdown(f"""
        <div class="ficha-cadastral" role="region" aria-label="Ficha Cadastral de {dados_distrito['distrito']}">
            <div class="ficha-kicker">CADASTRO TERRITORIAL • MUNICÍPIO DE SÃO PAULO</div>
            <div class="ficha-title">{dados_distrito['distrito']}</div>
            <div class="ficha-pills">
                <span class="ficha-pill">Zona {dados_distrito['zona']}</span>
                <span class="ficha-pill">Subpref. {dados_distrito['subprefeitura']}</span>
                {badge_idf}
            </div>
            <div class="ficha-grid">
                <div>
                    <div class="ficha-stat-label">População Residente</div>
                    <div class="ficha-stat-val">{dados_distrito['populacao']:,} hab</div>
                </div>
                <div>
                    <div class="ficha-stat-label">Renda Média Formal</div>
                    <div class="ficha-stat-val">R$ {dados_distrito['renda_media_formal']:,.2f}</div>
                </div>
                <div>
                    <div class="ficha-stat-label">Tempo Casa-Trabalho</div>
                    <div class="ficha-stat-val">{dados_distrito['tempo_deslocamento_min']:.1f} min</div>
                </div>
                <div>
                    <div class="ficha-stat-label">Equipamentos Ativos</div>
                    <div class="ficha-stat-val">{len(equipamentos_locais)} unidades</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #475569; display: flex; justify-content: space-between; align-items: center;">
                <span><strong>Índice de Deserto (IDF):</strong></span>
                <span style="font-size: 14px; font-weight: 800; color: #0F172A; font-variant-numeric: tabular-nums;">{idf_dist:.2f} / 10.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Atualizar Parecer Técnico", type="primary", use_container_width=True):
            st.rerun()

    with col_info_rapida:
        # Geração do Diagnóstico pela IA
        resultado_ia = gerar_diagnostico_ia(dados_distrito)
        st.markdown(resultado_ia["relatorio_markdown"])

        # Download do relatório em markdown
        st.download_button(
            label="Baixar Parecer Técnico (Markdown)",
            data=resultado_ia["relatorio_markdown"],
            file_name=f"parecer_tecnico_{distrito_escolhido.lower()}.md",
            mime="text/markdown"
        )


# -------------------------------------------------------------
# ABA 3: OBSERVATÓRIO COMPARATIVO
# -------------------------------------------------------------
with aba_graficos:
    st.markdown("#### Observatório Comparativo e Analítico de Disparidades")
    st.caption("Filtre por qualquer dimensão territorial, explore o construtor analítico bivariado e selecione visualizações multidimensionais.")

    sub_studio, sub_multidimensional = st.tabs([
        "Eixo A • Construtor Analítico Bivariado",
        "Eixo B • Matriz Multidimensional & Filtros"
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
                    <div class="kpi-card" role="region" aria-label="Maior {label_kpi}: {fmt_max} no distrito {dist_max}">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">MÁXIMO AMOSTRAL</span>
                            <span class="kpi-indicator-dot" style="background-color: #DC2626;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Maior {label_kpi[:18]}</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{fmt_max}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 100%; background-color: #DC2626;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Distrito: <strong>{dist_max}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="Menor {label_kpi}: {fmt_min} no distrito {dist_min}">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">MÍNIMO AMOSTRAL</span>
                            <span class="kpi-indicator-dot" style="background-color: #059669;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Menor {label_kpi[:18]}</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{fmt_min}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 45%; background-color: #059669;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Distrito: <strong>{dist_min}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="Média da amostra: {fmt_med}">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">MÉDIA AMOSTRAL</span>
                            <span class="kpi-indicator-dot" style="background-color: #0284C7;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Média da Seleção</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{fmt_med}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 72%; background-color: #0284C7;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Amostra: <strong>{len(df_mob_plot)} distritos</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k4:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="Disparidade territorial de {razao_disp:.1f} vezes">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">DISPARIDADE</span>
                            <span class="kpi-indicator-dot" style="background-color: #D97706;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Razão Máx / Mín</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{razao_disp:.1f}x</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 80%; background-color: #D97706;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Disparidade interna</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with k1:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="Total de {len(df_mob_plot)} distritos na amostra">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">AMOSTRA</span>
                            <span class="kpi-indicator-dot" style="background-color: #003399;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Distritos Analisados</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{len(df_mob_plot)}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: {(len(df_mob_plot)/96)*100:.0f}%; background-color: #003399;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>{(len(df_mob_plot)/96)*100:.1f}% da capital</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="População somada de {df_mob_plot['populacao'].sum():,.0f} habitantes">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">DEMOGRAFIA</span>
                            <span class="kpi-indicator-dot" style="background-color: #059669;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">População Amostral</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{df_mob_plot['populacao'].sum():,.0f}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 65%; background-color: #059669;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Habitantes residentes</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="{df_mob_plot['zona'].nunique()} regiões representadas">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">GEOGRAFIA</span>
                            <span class="kpi-indicator-dot" style="background-color: #D97706;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Zonas Presentes</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{df_mob_plot['zona'].nunique()}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: {(df_mob_plot['zona'].nunique()/5)*100:.0f}%; background-color: #D97706;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>De 5 macrorregiões</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with k4:
                    st.markdown(f"""
                    <div class="kpi-card" role="region" aria-label="{df_mob_plot['equipamentos_adesampa_ativos'].sum()} equipamentos ADE SAMPA ativos">
                        <div class="kpi-card-top">
                            <span class="kpi-source-tag">REDE PÚBLICA</span>
                            <span class="kpi-indicator-dot" style="background-color: #7C3AED;" aria-hidden="true"></span>
                        </div>
                        <div class="kpi-label">Equipamentos Ativos</div>
                        <div class="kpi-num-row">
                            <span class="kpi-value">{df_mob_plot['equipamentos_adesampa_ativos'].sum()}</span>
                        </div>
                        <div class="kpi-benchmark-bar" aria-hidden="true">
                            <div class="kpi-benchmark-fill" style="width: 50%; background-color: #7C3AED;"></div>
                        </div>
                        <div class="kpi-context-row">
                            <span>Unidades instaladas</span>
                        </div>
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
    st.markdown("#### Rede Municipal de Equipamentos ADE SAMPA")
    st.caption("Catálogo cadastral georreferenciado de unidades ativas da Rede Teia, FabLabs Livres e Postos de Atendimento na capital paulista.")

    # Resumo quantitativo em barra institucional
    total_eq = len(equipamentos)
    teias_qtd = sum(1 for e in equipamentos if "Teia" in e.get("tipo", ""))
    fablabs_qtd = sum(1 for e in equipamentos if "FabLab" in e.get("tipo", ""))
    postos_qtd = sum(1 for e in equipamentos if "Posto" in e.get("tipo", ""))
    cast_qtd = sum(1 for e in equipamentos if e.get("possui_sampa_cast"))

    st.markdown(f"""
    <div class="equip-summary-bar" role="region" aria-label="Síntese da Rede de Equipamentos ADE SAMPA">
        <div class="equip-stat-item">
            <span class="equip-stat-num">{total_eq}</span>
            <span class="equip-stat-txt">Unidades Ativas</span>
        </div>
        <div class="equip-stat-item">
            <span class="equip-stat-num" style="color: #2563EB;">{teias_qtd}</span>
            <span class="equip-stat-txt">Coworkings Teia</span>
        </div>
        <div class="equip-stat-item">
            <span class="equip-stat-num" style="color: #7C3AED;">{fablabs_qtd}</span>
            <span class="equip-stat-txt">FabLabs Livres SP</span>
        </div>
        <div class="equip-stat-item">
            <span class="equip-stat-num" style="color: #EA580C;">{postos_qtd}</span>
            <span class="equip-stat-txt">Postos de Atendimento</span>
        </div>
        <div class="equip-stat-item">
            <span class="equip-stat-num" style="color: #059669;">{cast_qtd}</span>
            <span class="equip-stat-txt">Com Estúdio Sampa Cast</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2.5, 1.5])
    with col_f1:
        tipo_filtro = st.multiselect(
            "Filtrar por Tipologia:",
            ["Rede Teia", "FabLab Livre", "Posto de Atendimento"],
            default=["Rede Teia", "FabLab Livre", "Posto de Atendimento"]
        )
    with col_f2:
        apenas_cast = st.checkbox("Apenas unidades com Estúdio Sampa Cast", value=False)

    equip_mostrados = [
        e for e in equipamentos
        if e.get("tipo") in tipo_filtro and (not apenas_cast or e.get("possui_sampa_cast"))
    ]

    for eq in equip_mostrados:
        tipo_cor = "#2563EB" if "Teia" in eq["tipo"] else ("#7C3AED" if "FabLab" in eq["tipo"] else "#EA580C")
        sampa_tag_txt = " • Sampa Cast" if eq.get("possui_sampa_cast") else ""
        sampa_badge = '<span style="background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 6px;">Estúdio Sampa Cast</span>' if eq.get("possui_sampa_cast") else ""
        
        with st.expander(f"{eq['nome']} — {eq['distrito']} ({eq['zona']}){sampa_tag_txt}"):
            c1, c2 = st.columns([1.8, 1.2])
            with c1:
                st.markdown(f"""
                <div style="margin-bottom: 6px;">
                    <span style="background: {tipo_cor}15; color: {tipo_cor}; border: 1px solid {tipo_cor}40; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">{eq['tipo']}</span>
                    <span style="background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-left: 4px;">{eq['categoria']}</span>
                    {sampa_badge}
                </div>
                <div style="font-size: 13px; color: #1E293B; margin-bottom: 4px;"><strong>Endereço:</strong> {eq['endereco']}</div>
                <div style="font-size: 13px; color: #1E293B;"><strong>Horário de Atendimento:</strong> {eq['horario']}</div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("<div style='font-size: 11.5px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 4px;'>Serviços Ofertados:</div>", unsafe_allow_html=True)
                chips_html = "".join([f'<span class="service-chip">{srv}</span>' for srv in eq.get("servicos", [])])
                st.markdown(f"<div>{chips_html}</div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# ABA 5: METODOLOGIA & SOBRE O EDITAL
# -------------------------------------------------------------
with aba_metodologia:
    st.markdown("""
    ### Sobre o Projeto e Cumprimento do Edital nº 005/2026
    
    Esta solução foi concebida sob medida para a **Prova Técnica Prática** do processo seletivo da **ADE SAMPA (Agência São Paulo de Desenvolvimento)**, cargo de **Assistente II - Dados e IA**.

    #### 1. Justificativa Pública do Tema
    A cidade de São Paulo possui um abismo socioeconômico histórico comprovado pelo *Mapa da Desigualdade*. Enquanto as oportunidades econômicas concentram-se no centro e no vetor sudoeste, as periferias concentram o empreendedorismo por sobrevivência e longos tempos de deslocamento diário. A **ADE SAMPA Territórios Inteligentes** permite que gestores públicos identifiquem onde alocar novas turmas da *Fábrica de Negócios*, novos coworkings públicos (*Rede Teia*) e mutirões de crédito (*CRED SAMPA*).

    #### 2. Metodologia do Índice de Deserto de Fomento (IDF)
    O **IDF** varia de `0.0` (atendido) a `10.0` (deserto crítico de fomento produtivo) e combina 4 dimensões oficiais:
    """)

    st.markdown("""<div class="method-grid-4">
<div class="method-card" style="border-top-color: #003399;">
<div class="method-card-pct">35%</div>
<div class="method-card-title">Vulnerabilidade de Renda</div>
<div class="method-card-desc">Relação proporcional entre a renda média formal do distrito e a referência salarial da capital (RAIS / CAGED).</div>
</div>
<div class="method-card" style="border-top-color: #0284C7;">
<div class="method-card-pct">25%</div>
<div class="method-card-title">Isolamento & Deslocamento</div>
<div class="method-card-desc">Tempo médio diário no trajeto casa-trabalho (Pesquisa OD Metrô). Penalidade severa para deslocamentos acima de 45 min.</div>
</div>
<div class="method-card" style="border-top-color: #D97706;">
<div class="method-card-pct">20%</div>
<div class="method-card-title">Densidade de Empregos Locais</div>
<div class="method-card-desc">Volume de postos de trabalho formais por 100 habitantes residentes. Mede a dependência centrípeta (bairro-dormitório).</div>
</div>
<div class="method-card" style="border-top-color: #DC2626;">
<div class="method-card-pct">20%</div>
<div class="method-card-title">Ausência de Equipamentos</div>
<div class="method-card-desc">Penalização para distritos sem coworkings Teia, FabLabs ou postos ADE SAMPA instalados no território.</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
    #### 3. Fontes de Dados Oficiais Utilizadas
    - **[GeoSampa — Mapa Digital da Cidade de São Paulo](https://geosampa.prefeitura.sp.gov.br/)**: Malha cartográfica vetorial dos 96 distritos, divisões de subprefeituras e camadas territoriais municipais (SIRGAS 2000).
    - **[Portal de Dados Abertos da Cidade de São Paulo (PMSP)](https://dados.prefeitura.sp.gov.br/)**: Catálogo aberto da Prefeitura com relação oficial de endereços e coordenadas dos equipamentos públicos municipais.
    - **[Mapa da Desigualdade (Rede Nossa São Paulo / Instituto Cidades Sustentáveis)](https://www.nossasaopaulo.org.br/)**: Levantamento anual com indicadores distritais de remuneração média, tempo de deslocamento e postos de trabalho.
    - **[IBGE — Censo Demográfico e Estatísticas Territoriais](https://censo2022.ibge.gov.br/)**: Dados demográficos e contagem populacional consolidada por setor e distrito censitário.
    - **[Fundação SEADE — Sistema Estadual de Análise de Dados](https://repositorio.seade.gov.br/)**: Projeções demográficas, estatísticas socioeconômicas e repositório de dados abertos paulistas.
    - **[Portal Oficial da ADE SAMPA](https://adesampa.com.br/)**: Programas de fomento, equipamentos públicos (Rede Teia, FabLabs Livres, Postos ADE SAMPA), capacitações e microcrédito orientado (CRED SAMPA).

    #### 4. Mapa do Site & Recursos de Apoio
    - **Guia do Usuário e Mapa do Site (`SITEMAP.md`)**: O repositório inclui um guia visual completo com roteiro de 5 minutos para a banca avaliadora, catálogo de todos os 7 gráficos e navegação tela a tela.
    - **Exportação Executiva Multi-Formato**: Suporte a download de gráficos em **PNG em alta resolução (300 DPI)**, tabelas em **CSV estruturado para Excel (`UTF-8 com BOM`)** e pareceres de IA em **Markdown**.
    - **Acessibilidade Digital (WCAG 2.1 AA)**: Marcadores semânticos, navegação por teclado (`Tab`), skip-link invisível e textos alternativos (*alt-text*) para leitura inclusiva e auditada.

    #### 5. Dicionário Normativo de Siglas & Acrônimos Oficiais
    Para assegurar a transparência ativa, a auditabilidade da banca examinadora e o pleno entendimento dos indicadores sem necessidade de conhecimento prévio, a tabela a seguir consolida todas as siglas empregadas na plataforma:

    | Sigla / Termo | Nome por Extenso / Significado Oficial | Órgão / Entidade Gestora | Aplicação na Plataforma |
    | :--- | :--- | :--- | :--- |
    | **ADE SAMPA** | Agência São Paulo de Desenvolvimento | PMSP / SMDET | Agência pública municipal operadora dos equipamentos de fomento e crédito orientado. |
    | **IDF** | Índice de Deserto de Fomento | Formulador da Metodologia / Edital | Indicador sintético (0 a 10) que quantifica a carência territorial de serviços de desenvolvimento econômico. |
    | **PMSP** | Prefeitura do Município de São Paulo | Poder Executivo Municipal | Ente federativo mantenedor das políticas públicas e dos dados abertos municipais. |
    | **SMDET** | Secretaria Municipal de Desenvolvimento Econômico e Trabalho | PMSP | Secretaria da Prefeitura de São Paulo à qual a ADE SAMPA é vinculada. |
    | **SEADE** | Fundação Sistema Estadual de Análise de Dados | Governo do Estado de SP | Órgão estatístico paulista responsável pelas projeções e dados demográficos e econômicos. |
    | **IBGE** | Instituto Brasileiro de Geografia e Estatística | Ministério do Planejamento / Governo Federal | Instituto responsável pelo Censo Demográfico 2022 e contagem oficial da população. |
    | **CENSO 2022** | Censo Demográfico Nacional 2022 | IBGE | Operação censitária decenal que mapeou a população residente e os domicílios brasileiros. |
    | **RAIS** | Relação Anual de Informações Sociais | Ministério do Trabalho e Emprego (MTE) | Registro administrativo que mapeia vínculos empregatícios formais e massa salarial por distrito. |
    | **CAGED** | Cadastro Geral de Empregados e Desempregados | Ministério do Trabalho e Emprego (MTE) | Registro mensal de admissões e desligamentos sob regime da CLT, balizando a renda média formal. |
    | **OD METRÔ** | Pesquisa Origem e Destino da Cia. do Metropolitano | Metrô de São Paulo / STM-SP | Pesquisa decenal que mensura tempos de viagem, modos de transporte e deslocamento pendular casa-trabalho. |
    | **GeoSampa** | Mapa Digital Oficial da Cidade de São Paulo | PMSP / SMUL | Plataforma cartográfica geoespacial aberta do município com malha vetorial dos 96 distritos. |
    | **SIRGAS 2000** | Sistema de Referência Geocêntrico para as Américas 2000 | IBGE / Cartografia Oficial | Datum geodésico e referencial cartográfico oficial do Brasil e do município de São Paulo. |
    | **WCAG 2.1 AA** | Web Content Accessibility Guidelines (Nível AA) | W3C / WAI | Diretrizes internacionais de acessibilidade na web adotadas para contraste, fontes e leitores de tela. |
    | **MEI** | Microempreendedor Individual | Receita Federal / Comitê Simples Nacional | Categoria jurídica empresarial atendida prioritariamente pelos programas e capacitações da ADE SAMPA. |
    | **Subp. / Subpref.** | Subprefeitura Municipal | PMSP / SMSUB | As 32 divisões administrativas regionais que agrupam os 96 distritos da capital. |
    | **RMSP** | Região Metropolitana de São Paulo | EMPLASA / Governo de SP | Aglomeração urbana de 39 municípios paulistas que polarizam fluxos de deslocamento e trabalho. |
    """)

    # Botão de download do PDF ilustrado na Aba 5
    pdf_path_aba5 = ROOT_DIR / "data" / "mapa_do_site_adesampa.pdf"
    if pdf_path_aba5.exists():
        with open(pdf_path_aba5, "rb") as f_pdf5:
            pdf_bytes_aba5 = f_pdf5.read()
        col_pdf_b, _ = st.columns([1.6, 2.4])
        with col_pdf_b:
            st.download_button(
                label="Baixar Guia Visual & Mapa do Site (PDF Ilustrado)",
                data=pdf_bytes_aba5,
                file_name="mapa_do_site_adesampa.pdf",
                mime="application/pdf",
                key="dl_btn_sitemap_pdf_aba5",
                use_container_width=True,
                help="Download do documento PDF oficial com capturas de tela e roteiro completo."
            )


# -------------------------------------------------------------
# 7. RODAPÉ INSTITUCIONAL (PMSP / ADE SAMPA)
# -------------------------------------------------------------
ambiente_execucao = detectar_ambiente()
st.markdown(f"""
<footer class="civic-footer" role="contentinfo" aria-label="Informações Institucionais e Conformidade Legal">
    <div class="civic-footer-inner">
        <div class="civic-footer-col">
            <div class="footer-title">PREFEITURA DA CIDADE DE SÃO PAULO</div>
            <div class="footer-sub">Secretaria Municipal de Desenvolvimento Econômico e Trabalho (SMDET)</div>
            <div class="footer-sub">ADE SAMPA — Agência São Paulo de Desenvolvimento</div>
            <div class="footer-meta">Edital de Seleção Pública nº 005/2026 • Assistente II - Dados e IA</div>
        </div>
        <div class="civic-footer-col">
            <div class="footer-title">REFERENCIAIS TÉCNICOS & CARTOGRÁFICOS</div>
            <div class="footer-sub">Base Cartográfica: GeoSampa • Sistema SIRGAS 2000 / UTM 23S</div>
            <div class="footer-sub">Fontes Oficiais: Censo 2022 • RAIS/CAGED 2024 • Pesquisa OD Metrô • SEADE</div>
            <div class="footer-meta">Conformidade: Padrões WCAG 2.1 Nível AA • LGPD (Lei nº 13.709/2018)</div>
        </div>
        <div class="civic-footer-col">
            <div class="footer-title">TELEMETRIA & AMBIENTE</div>
            <div class="footer-sub">Ambiente Ativo: <strong>{ambiente_execucao}</strong></div>
            <div class="footer-sub">Arquitetura: Streamlit Engine • Folium Leaflet • Plotly WebGL</div>
            <div class="footer-meta">Repositório: LucasArtoni1983/adesampa-territorios-inteligentes (MIT)</div>
        </div>
    </div>
</footer>
""", unsafe_allow_html=True)
