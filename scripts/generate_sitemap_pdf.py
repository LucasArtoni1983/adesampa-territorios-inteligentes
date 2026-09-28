"""
Gerador de PDF de Alta Qualidade: Mapa do Site & Guia Visual de Navegação
ADE SAMPA Territórios Inteligentes — Edital nº 005/2026
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent.parent
SCREENS_DIR = ROOT_DIR / "docs" / "assets" / "screens"
LOGO_PATH = ROOT_DIR / "ade-300x300-1-300x300-1-300x300.png"
OUTPUT_PDF = ROOT_DIR / "docs" / "mapa_do_site_adesampa.pdf"
OUTPUT_APP_PDF = ROOT_DIR / "data" / "mapa_do_site_adesampa.pdf"

# Cores da Identidade Visual ADE SAMPA / PMSP
PRIMARY = colors.HexColor("#1E3A8A")     # Azul institucional profundo
SECONDARY = colors.HexColor("#0284C7")   # Azul tecnológico ciano
ACCENT = colors.HexColor("#D97706")      # Âmbar / Laranja fomento
TEXT_DARK = colors.HexColor("#0F172A")   # Ardósia escuro
TEXT_MUTED = colors.HexColor("#475569")  # Cinza intermediário
BG_LIGHT = colors.HexColor("#F8FAFC")    # Fundo suave
BORDER_COLOR = colors.HexColor("#E2E8F0")# Borda suave
WHITE = colors.HexColor("#FFFFFF")
GREEN = colors.HexColor("#059669")
RED = colors.HexColor("#DC2626")


class NumberedCanvas(canvas.Canvas):
    """Canvas com numeração de páginas 'Página X de Y' e rodapé institucional."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        
        # Cabeçalho sutil (a partir da página 2)
        if self._pageNumber > 1:
            self.drawString(54, 805, "ADE SAMPA Territórios Inteligentes — Mapa do Site & Guia Visual")
            self.drawRightString(541, 805, "Edital nº 005/2026")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 798, 541, 798)
            
        # Rodapé
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, "Prefeitura de São Paulo • Secretaria de Desenvolvimento Econômico e Trabalho • ADE SAMPA")
        self.drawRightString(541, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def criar_pdf_mapa_site():
    os.makedirs(OUTPUT_PDF.parent, exist_ok=True)
    os.makedirs(OUTPUT_APP_PDF.parent, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    # Estilos Tipográficos Customizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=TEXT_MUTED,
        spaceAfter=14
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=TEXT_DARK,
        leftIndent=12,
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        'ImageCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1, # Centralizado
        spaceBefore=4,
        spaceAfter=8
    )
    
    box_header_style = ParagraphStyle(
        'BoxHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=PRIMARY
    )

    story = []

    # =========================================================================
    # PÁGINA 1: CAPA, VISÃO GERAL & JORNADA DA BANCA AVALIADORA
    # =========================================================================
    
    # Cabeçalho da Capa com Logo e Títulos
    if LOGO_PATH.exists():
        img_logo = Image(str(LOGO_PATH), width=50, height=50)
        hdr_table = Table([[img_logo, [
            Paragraph("ADE SAMPA Territórios Inteligentes", title_style),
            Paragraph("Mapa do Site & Guia Visual de Navegação da Aplicação • Edital de Seleção nº 005/2026", subtitle_style)
        ]]], colWidths=[60, 445])
        hdr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(hdr_table)
    else:
        story.append(Paragraph("ADE SAMPA Territórios Inteligentes", title_style))
        story.append(Paragraph("Mapa do Site & Guia Visual de Navegação da Aplicação", subtitle_style))

    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=4, spaceAfter=12))

    # Caixa de Destaque: Apresentação da Plataforma
    intro_html = (
        "<b>A Plataforma ADE SAMPA Territórios Inteligentes</b> é uma solução web funcional desenvolvida para apoiar "
        "o planejamento territorial da <b>Prefeitura de São Paulo</b> e da <b>ADE SAMPA</b>. A aplicação georreferencia os 96 "
        "distritos da capital, analisa o <b>Índice de Deserto de Fomento (IDF)</b>, calcula áreas de cobertura dos equipamentos "
        "públicos (Rede Teia, FabLabs Livres, Postos ADE SAMPA) e fornece um <b>Copiloto de IA</b> para geração automatizada "
        "de pareceres técnicos e recomendações de políticas públicas."
    )
    intro_table = Table([[Paragraph(intro_html, body_style)]], colWidths=[505])
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 10))

    # Tabela de Indicadores Gerais da Cidade
    story.append(Paragraph("Indicadores Macrotterritoriais em Destaque na Plataforma", h2_style))
    kpi_data = [
        [
            Paragraph("<b>Populacao da Capital</b><br/><font size='11' color='#1E3A8A'><b>12.202.458 hab</b></font><br/><font size='7' color='#475569'>Censo Demografico IBGE</font>", body_style),
            Paragraph("<b>Renda Media Formal</b><br/><font size='11' color='#059669'><b>R$ 4.708,55</b></font><br/><font size='7' color='#475569'>Media Ponderada SP</font>", body_style),
            Paragraph("<b>Tempo Medio ao Trabalho</b><br/><font size='11' color='#D97706'><b>45,2 min</b></font><br/><font size='7' color='#475569'>Deslocamento diario</font>", body_style),
            Paragraph("<b>Equipamentos ADE SAMPA</b><br/><font size='11' color='#6D28D9'><b>24 unidades</b></font><br/><font size='7' color='#475569'>Teias, FabLabs e Postos</font>", body_style),
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[126, 126, 126, 127])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 12))

    # Roteiro Expresso da Banca Avaliadora
    story.append(Paragraph("Roteiro Expresso de Avaliacao Tecnica (5 Minutos)", h2_style))
    story.append(Paragraph("Para a validacao agil e autossuficiente de todos os criterios do Edital no 005/2026:", body_style))
    
    banca_steps = [
        "<b>Passo 1 (Aba 1 - Mapa):</b> Altere na barra lateral a <i>Regiao da Capital</i> para <b>Leste</b> e a <i>Subprefeitura</i> para <b>Itaquera</b>. Observe o realce visual dos poligonos e o zoom automatico (<code>fit_bounds</code>) aos limites da selecao.",
        "<b>Passo 2 (Aba 2 - Copiloto de IA):</b> Selecione um distrito periferico (ex: <b>Brasilandia</b>). Avalie a sintese dos gargalos locais e baixe o parecer tecnico em Markdown.",
        "<b>Passo 3 (Aba 3 - Studio de Graficos):</b> Explore os 7 tipos de graficos. Teste a ordenacao ativa no <i>Grafico de Linhas</i> e a ordenacao adaptativa desabilitada no <i>Grafico de Pizza</i>. Clique em <b>Baixar Grafico em Alta Resolucao (PNG)</b>.",
        "<b>Passo 4 (Aba 4 - Equipamentos):</b> Filtre unidades marcando <code>Apenas unidades com Estudio Sampa Cast</code>.",
        "<b>Passo 5 (Aba 5 - Metodologia):</b> Confira a formulacao matematica do IDF, fontes oficiais de dados e diretrizes de IA."
    ]
    for step in banca_steps:
        story.append(Paragraph(f"&bull; {step}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: ABA 1 — MAPA TERRITORIAL INTERATIVO
    # =========================================================================
    story.append(Paragraph("Aba 1: Mapa Territorial Interativo & Pontos Cegos", title_style))
    story.append(Paragraph("Visualizacao geoespacial vetorial dos 96 distritos paulistanos com camadas de vulnerabilidade e equipamentos publicos.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=8))

    img_mapa = SCREENS_DIR / "01_mapa_territorial.png"
    if img_mapa.exists():
        story.append(Image(str(img_mapa), width=505, height=265))
        story.append(Paragraph("Figura 1: Captura fidedigna da Aba 1 exibindo o mapa de calor vetorial do IDF, raios de cobertura e tabela.", caption_style))

    story.append(Paragraph("Funcionalidades Chave do Modulo Cartografico:", h2_style))
    story.append(Paragraph("&bull; <b>Poligonos Tematicos por IDF:</b> Os 96 distritos de SP sao coloridos conforme o Indice de Deserto de Fomento: Deserto Critico (IDF &ge; 7.5), Deserto Moderado (5.5 a 7.4), Em Cobertura (3.5 a 5.4) e Polo Consolidado (&lt; 3.5).", bullet_style))
    story.append(Paragraph("&bull; <b>Sincronizacao Dinamica e Auto-Zoom:</b> Ao filtrar zonas ou subprefeituras na barra lateral, os distritos correspondentes sao destacados com contorno forte (3px), o restante da cidade e atenuado em cinza suave e a camera aproxima automaticamente via <code>fit_bounds</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Marcadores e Circulos de Cobertura:</b> Plotagem das unidades da Rede Teia (laptop azul), FabLabs Livres (cubo roxo) e Postos ADE SAMPA (maleta laranja), com circulos de raio de 2.5 km indicando alcance de pedestre/transporte local.", bullet_style))
    story.append(Paragraph("&bull; <b>Exportacao em CSV Estruturado:</b> Botao dedicado na barra lateral e acima da tabela para baixar os distritos filtrados com compatibilidade nativa para o Microsoft Excel (codificacao UTF-8 com BOM e separador ponto e virgula).", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: ABA 2 — COPILOTO DE IA & DIAGNÓSTICO
    # =========================================================================
    story.append(Paragraph("Aba 2: Copiloto de IA & Diagnostico Territorial", title_style))
    story.append(Paragraph("Assistente analitico inteligente para apoio a tomada de decisao de gestores da ADE SAMPA e SMDET.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=8))

    img_ia = SCREENS_DIR / "02_copiloto_ia.png"
    if img_ia.exists():
        story.append(Image(str(img_ia), width=505, height=270))
        story.append(Paragraph("Figura 2: Captura fidedigna do Parecer Tecnico gerado pela inteligencia analitica com diretrizes de intervencao publica.", caption_style))

    story.append(Paragraph("Destaques do Modulo de Inteligencia Artificial:", h2_style))
    story.append(Paragraph("&bull; <b>Ficha Tecnica Consolidada:</b> Exibe populacao estimada, zona, subprefeitura, renda media formal, tempo de deslocamento ao trabalho e equipamentos municipais ativos no distrito selecionado.", bullet_style))
    story.append(Paragraph("&bull; <b>Identificacao Algoritmica de Gargalos:</b> O motor avalia o perfil socioeconomico e classifica carencias severas (ex: tempo de deslocamento &gt; 60 min, baixa densidade de microcredito formal, ausencia de espacos publicos de coworking).", bullet_style))
    story.append(Paragraph("&bull; <b>Diretrizes Estrategicas para Gestao:</b> Recomendacoes personalizadas para o Plano de Metas da cidade: alocacao de unidades moveis, implantacao prioritaria da Rede Teia, editais locais da Fabrica de Negocios e mutiroes de microcredito CRED SAMPA.", bullet_style))
    story.append(Paragraph("&bull; <b>Exportacao de Parecer Tecnico (Markdown):</b> O gestor publico pode baixar o relatorio executivo completo em formato <code>.md</code> com um unico clique para juntada direta a processos administrativos e despachos oficiais.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: ABA 3 — OBSERVATÓRIO COMPARATIVO & STUDIO
    # =========================================================================
    story.append(Paragraph("Aba 3: Observatorio Comparativo & Studio Dinamico", title_style))
    story.append(Paragraph("Construtor analitico livre com 7 tipos de graficos e exportacao em PNG de 300 DPI e CSV para Excel.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=8))

    img_studio = SCREENS_DIR / "03_studio_mobilidade.png"
    if img_studio.exists():
        story.append(Image(str(img_studio), width=505, height=270))
        story.append(Paragraph("Figura 3: Captura fidedigna do Studio Construtor com controles dinamicos de eixos, ordenacao adaptativa e botoes de exportacao.", caption_style))

    story.append(Paragraph("Recursos do Studio Dinamico de Mobilidade:", h2_style))
    story.append(Paragraph("&bull; <b>7 Modelos Visuais:</b> Grafico de Linhas (com marcadores), Barras Horizontais, Barras Verticais, Pirulito (Lollipop), Area Preenchida, Pizza/Donut e Dispersao Cartesiana (Scatter).", bullet_style))
    story.append(Paragraph("&bull; <b>Ordenacao Inteligente Adaptativa:</b> Habilita escolha de sentido Ascendente ou Decrescente em graficos sequenciais/rankings; bloqueia com aviso metodologico em graficos de proporcao (Pizza) e coordenadas (Dispersao).", bullet_style))
    story.append(Paragraph("&bull; <b>Exportacao PNG em Alta Definicao:</b> Botao sob demanda para download imediato da imagem em 300 DPI equivalente (1200x650px a 2x DPI), perfeita para apresentacoes e relatorios oficiais.", bullet_style))
    story.append(Paragraph("&bull; <b>Observatorio Multidimensional:</b> Graficos integrados de correlacao entre tempo de deslocamento vs remuneracao media formal, ranking dos desertos mais criticos e matriz de vulnerabilidade multidimensional.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: ABAS 4 E 5 — CATÁLOGO, METODOLOGIA & RECURSOS
    # =========================================================================
    story.append(Paragraph("Abas 4 e 5: Catalogo de Unidades & Metodologia Oficial", title_style))
    story.append(Paragraph("Consulta de equipamentos publicos, transparencia estatistica e conformidade estrita com o Edital no 005/2026.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=8))

    # Tabela com as 2 capturas lado a lado
    img_eq = SCREENS_DIR / "04_rede_equipamentos.png"
    img_met = SCREENS_DIR / "05_metodologia_edital.png"
    
    if img_eq.exists() and img_met.exists():
        img_row = [
            [Image(str(img_eq), width=245, height=155), Image(str(img_met), width=245, height=155)],
            [Paragraph("Figura 4: Catalogo de Equipamentos e filtro Sampa Cast.", caption_style),
             Paragraph("Figura 5: Documentacao de Metodologia e Edital.", caption_style)]
        ]
        t_dual = Table(img_row, colWidths=[250, 255])
        t_dual.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t_dual)
        story.append(Spacer(1, 6))

    story.append(Paragraph("Fundamentacao Metodologica do Indice de Deserto de Fomento (IDF):", h2_style))
    story.append(Paragraph("O IDF varia de 0.0 a 10.0 e pondera 4 dimensoes consolidadas do desenvolvimento economico paulistano:", body_style))
    story.append(Paragraph("&bull; <b>Vulnerabilidade de Renda (35%):</b> Distancia proporcional a remuneracao de referencia municipal.", bullet_style))
    story.append(Paragraph("&bull; <b>Tempo de Deslocamento ao Trabalho (25%):</b> Penalidade escalonada para trajetos medios superiores a 45 minutos.", bullet_style))
    story.append(Paragraph("&bull; <b>Densidade Local de Empregos (20%):</b> Razao de postos formais por 100 habitantes (caracterizacao de bairro-dormitorio).", bullet_style))
    story.append(Paragraph("&bull; <b>Carencia de Equipamentos Ativos (20%):</b> Penalidade maxima para distritos com zero unidades ADE SAMPA instaladas.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Instrucoes de Execucao Expressa em 1 Clique (Banca Avaliadora):", h2_style))
    story.append(Paragraph("&bull; <b>No Windows:</b> De um duplo clique no arquivo <code>run.bat</code> na raiz do projeto.", bullet_style))
    story.append(Paragraph("&bull; <b>No Linux / macOS:</b> Execute <code>chmod +x run.sh && ./run.sh</code> no terminal.", bullet_style))
    story.append(Paragraph("&bull; <b>Acesso Local:</b> Abra o navegador em <code>http://localhost:8501</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Suite de Testes:</b> Execute <code>pytest</code> no terminal para conferir os 18 testes automatizados aprovados.", bullet_style))

    # Constrói o PDF com numeração de páginas profissional
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Copia para a pasta data/ para download direto na aplicação web
    import shutil
    shutil.copyfile(OUTPUT_PDF, OUTPUT_APP_PDF)
    
    print(f"[OK] PDF gerado com sucesso em: {OUTPUT_PDF}")
    print(f"[OK] Cópia para aplicação em: {OUTPUT_APP_PDF}")

if __name__ == "__main__":
    criar_pdf_mapa_site()
