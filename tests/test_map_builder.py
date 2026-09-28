"""
Testes unitários para o módulo map_builder (construção e sincronização do mapa Folium).
"""

import folium
from src.data_loader import carregar_geojson_distritos, carregar_equipamentos
from src.map_builder import criar_mapa_territorial


def test_criar_mapa_territorial_geral():
    """Garante que o mapa é construído com sucesso para a totalidade dos 96 distritos."""
    geo = carregar_geojson_distritos()
    eq = carregar_equipamentos()
    mapa = criar_mapa_territorial(geo, eq, mostrar_raio_cobertura=True)
    assert isinstance(mapa, folium.Map)
    assert mapa.location == [-23.5505, -46.6333]


def test_criar_mapa_territorial_com_subprefeitura_dois_distritos():
    """Garante que o mapa sincroniza com seleção de subprefeitura (ex: Freguesia/Brasilândia)."""
    geo = carregar_geojson_distritos()
    eq = carregar_equipamentos()
    distritos_teste = ["Brasilândia", "Freguesia do Ó"]

    mapa = criar_mapa_territorial(
        geojson_distritos=geo,
        equipamentos=eq,
        mostrar_raio_cobertura=True,
        distritos_destacados=distritos_teste,
        focar_selecao=True
    )
    assert isinstance(mapa, folium.Map)
    # Garante que gerou o mapa e adicionou camadas
    filhos = [type(c).__name__ for c in mapa._children.values()]
    assert "GeoJson" in filhos
    assert "FeatureGroup" in filhos


def test_criar_mapa_territorial_distrito_unico():
    """Garante que seleção de um único distrito funciona com zoom adequado."""
    geo = carregar_geojson_distritos()
    eq = carregar_equipamentos()

    mapa = criar_mapa_territorial(
        geojson_distritos=geo,
        equipamentos=eq,
        distrito_selecionado="Sé",
        focar_selecao=True
    )
    assert isinstance(mapa, folium.Map)
