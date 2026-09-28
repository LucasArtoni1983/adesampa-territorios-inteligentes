"""
Script para capturar telas fidedignas da aplicação Streamlit em execução
"""
import os
import time
from playwright.sync_api import sync_playwright

output_dir = "docs/assets/screens"
os.makedirs(output_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 920})
    page = context.new_page()
    
    print("[1/6] Navegando para http://localhost:8501...")
    page.goto("http://localhost:8501", wait_until="networkidle")
    page.wait_for_timeout(4000)
    
    # 1. Visão Geral e Mapa Territorial (Aba 1)
    print("[2/6] Capturando Aba 1: Mapa Territorial Interativo...")
    page.screenshot(path=os.path.join(output_dir, "01_mapa_territorial.png"))
    
    # Busca todas as abas principais
    tabs = page.get_by_role("tab")
    count = tabs.count()
    print(f"Total de abas encontradas: {count}")
    
    # 2. Aba 2: Copiloto de IA & Diagnóstico
    print("[3/6] Capturando Aba 2: Copiloto de IA & Diagnóstico...")
    page.get_by_role("tab", name="🤖 Copiloto de IA & Diagnóstico").click()
    page.wait_for_timeout(3500)
    page.screenshot(path=os.path.join(output_dir, "02_copiloto_ia.png"))
    
    # 3. Aba 3: Observatório Comparativo
    print("[4/6] Capturando Aba 3: Observatório Comparativo...")
    page.get_by_role("tab", name="📈 Observatório Comparativo").click()
    page.wait_for_timeout(3500)
    page.screenshot(path=os.path.join(output_dir, "03_studio_mobilidade.png"))
    
    # 4. Aba 4: Rede de Equipamentos ADE SAMPA
    print("[5/6] Capturando Aba 4: Rede de Equipamentos...")
    page.get_by_role("tab", name="🏢 Rede de Equipamentos ADE SAMPA").click()
    page.wait_for_timeout(3000)
    page.screenshot(path=os.path.join(output_dir, "04_rede_equipamentos.png"))
    
    # 5. Aba 5: Metodologia & Edital
    print("[6/6] Capturando Aba 5: Metodologia & Edital...")
    page.get_by_role("tab", name="📑 Metodologia & Edital").click()
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(output_dir, "05_metodologia_edital.png"))
    
    browser.close()

print("SUCESSO: Todas as 5 telas foram capturadas em", output_dir)
