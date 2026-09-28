"""
Módulo de visualização cartográfica interativa com Folium.
Renderiza malha vetorial dos distritos, indicadores de calor e equipamentos ADE SAMPA.
"""

from typing import Any, Dict, List, Optional, Set
import folium
from folium.plugins import Fullscreen, MarkerCluster


def criar_mapa_territorial(
    geojson_distritos: Dict[str, Any],
    equipamentos: List[Dict[str, Any]],
    mostrar_raio_cobertura: bool = True,
    distrito_selecionado: Optional[str] = None,
    distritos_destacados: Optional[List[str]] = None,
    focar_selecao: bool = True,
    **kwargs
) -> folium.Map:
    """
    Constrói o mapa interativo de São Paulo com camadas temáticas:
    1. Polígonos dos 96 distritos com destaque dinâmico para seleção atual (Zona/Subprefeitura).
    2. Marcadores das unidades ADE SAMPA (Teias, FabLabs e Postos).
    3. Círculos de raio de cobertura (2.5 km) demonstrando alcance das unidades.
    4. Auto-enquadramento (fit_bounds) para aproximar a visão na região filtrada.
    """
    # Consolidação de distritos em foco
    destacados_lista = list(distritos_destacados) if distritos_destacados is not None else []
    if distrito_selecionado and distrito_selecionado != "Todos" and distrito_selecionado not in destacados_lista:
        destacados_lista.append(distrito_selecionado)

    total_distritos_geojson = len(geojson_distritos.get("features", []))
    filtro_ativo = bool(destacados_lista and len(destacados_lista) < total_distritos_geojson)
    destacados_set: Set[str] = set(destacados_lista) if filtro_ativo else set()

    # Centro padrão aproximado da cidade de São Paulo
    centro_sp = [-23.5505, -46.6333]
    zoom_inicial = 11
    bounds_selecao = None

    # Cálculo da Bounding Box e Centro para os distritos selecionados
    if filtro_ativo and focar_selecao:
        lats = []
        lons = []
        for feat in geojson_distritos.get("features", []):
            nome = feat.get("properties", {}).get("nome")
            if nome in destacados_set:
                geom = feat.get("geometry", {})
                gtype = geom.get("type", "")
                coords = geom.get("coordinates", [])
                if gtype == "Polygon":
                    for anel in coords:
                        for pt in anel:
                            lons.append(pt[0])
                            lats.append(pt[1])
                elif gtype == "MultiPolygon":
                    for poly in coords:
                        for anel in poly:
                            for pt in anel:
                                lons.append(pt[0])
                                lats.append(pt[1])

        if lats and lons:
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            centro_sp = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
            if abs(max_lat - min_lat) < 0.005 and abs(max_lon - min_lon) < 0.005:
                zoom_inicial = 14
            else:
                bounds_selecao = [[min_lat, min_lon], [max_lat, max_lon]]

    mapa = folium.Map(
        location=centro_sp,
        zoom_start=zoom_inicial,
        tiles="OpenStreetMap",
        control_scale=True
    )
    Fullscreen().add_to(mapa)

    if bounds_selecao:
        mapa.fit_bounds(bounds_selecao, padding=(25, 25))

    # Injeta CSS para bordas arredondadas e acabamento suave em tooltips e popups
    css_arredondado = """
    <style>
        .leaflet-tooltip {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-size: 12px !important;
            line-height: 1.4 !important;
        }
        .leaflet-tooltip-top:before,
        .leaflet-tooltip-bottom:before,
        .leaflet-tooltip-left:before,
        .leaflet-tooltip-right:before {
            border-top-color: #CBD5E1 !important;
        }
        .leaflet-popup-content-wrapper {
            border-radius: 14px !important;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16) !important;
            border: 1px solid #E2E8F0 !important;
            padding: 4px !important;
        }
        .leaflet-popup-tip {
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16) !important;
        }
    </style>
    """
    mapa.get_root().html.add_child(folium.Element(css_arredondado))

    # 1. Camada de Polígonos dos Distritos
    def estilo_poligono(feature):
        cor = feature.get("properties", {}).get("cor", "#3B82F6")
        nome = feature.get("properties", {}).get("nome")

        if filtro_ativo:
            if nome in destacados_set:
                return {
                    "fillColor": cor,
                    "color": "#0F172A",
                    "weight": 3.0,
                    "fillOpacity": 0.75,
                }
            else:
                return {
                    "fillColor": "#F1F5F9",
                    "color": "#CBD5E1",
                    "weight": 0.8,
                    "fillOpacity": 0.20,
                }
        else:
            return {
                "fillColor": cor,
                "color": "#64748B",
                "weight": 1,
                "fillOpacity": 0.50,
            }

    folium.GeoJson(
        geojson_distritos,
        name="Distritos de SP (Índice de Fomento)",
        style_function=estilo_poligono,
        tooltip=folium.GeoJsonTooltip(
            fields=["nome", "subprefeitura", "zona", "renda", "desloc", "indice_deserto", "classificacao"],
            aliases=[
                "Distrito:",
                "Subprefeitura:",
                "Zona:",
                "Renda Média (R$):",
                "Tempo Deslocamento (min):",
                "Índice de Deserto (0-10):",
                "Status:"
            ],
            localize=True,
            sticky=True,
            style="""
                background-color: #FFFFFF;
                color: #0F172A;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 12px;
                padding: 10px 14px;
                border-radius: 12px;
                border: 1px solid #CBD5E1;
                box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
                line-height: 1.5;
            """
        )
    ).add_to(mapa)

    # 2. Camada de Raios de Cobertura (Isócrona aproximada de 2.5 km)
    if mostrar_raio_cobertura:
        fg_raios = folium.FeatureGroup(name="Raios de Cobertura (2.5 km)")
        for eq in equipamentos:
            lat = eq.get("latitude")
            lon = eq.get("longitude")
            tipo = eq.get("tipo", "")
            if lat and lon and tipo in ["Rede Teia", "FabLab Livre"]:
                folium.Circle(
                    location=[lat, lon],
                    radius=2500,  # 2.5 km em metros
                    color="#0055A5",
                    weight=1,
                    fill=True,
                    fill_color="#0055A5",
                    fill_opacity=0.08,
                    tooltip=folium.Tooltip(
                        f"Raio de atendimento: {eq.get('nome')}",
                        style="border-radius: 8px; font-family: sans-serif; font-size: 11px; padding: 4px 8px; background-color: #FFFFFF; color: #0F172A; border: 1px solid #CBD5E1;"
                    )
                ).add_to(fg_raios)
        fg_raios.add_to(mapa)

    # 3. Camada de Marcadores dos Equipamentos ADE SAMPA
    fg_equipamentos = folium.FeatureGroup(name="Equipamentos ADE SAMPA")
    for eq in equipamentos:
        lat = eq.get("latitude")
        lon = eq.get("longitude")
        if not (lat and lon):
            continue

        tipo = eq.get("tipo", "Posto de Atendimento")
        nome = eq.get("nome", "Equipamento")
        endereco = eq.get("endereco", "")
        horario = eq.get("horario", "")
        sampa_cast = "🎙️ Possui Estúdio Sampa Cast" if eq.get("possui_sampa_cast") else ""
        servicos = "<br>• " + "<br>• ".join(eq.get("servicos", []))

        # Cores e ícones por categoria
        if tipo == "Rede Teia":
            cor_marcador = "blue"
            icone = "laptop"
        elif tipo == "FabLab Livre":
            cor_marcador = "purple"
            icone = "cube"
        else:
            cor_marcador = "orange"
            icone = "briefcase"

        html_popup = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 260px; border-radius: 10px; padding: 2px;">
            <h4 style="margin: 0 0 6px 0; color: #1E40AF; font-size: 14px;">{nome}</h4>
            <span style="background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">{tipo}</span>
            <p style="margin: 8px 0 4px 0; font-size: 12px; color: #334155; line-height: 1.4;"><strong>Endereço:</strong> {endereco}</p>
            <p style="margin: 4px 0; font-size: 12px; color: #334155;"><strong>Horário:</strong> {horario}</p>
            {f'<p style="margin: 4px 0; font-size: 12px; color: #16A34A; font-weight: bold;">{sampa_cast}</p>' if sampa_cast else ''}
            <div style="margin-top: 6px; font-size: 11px; color: #475569; border-top: 1px solid #F1F5F9; padding-top: 6px;">
                <strong>Serviços Ofertados:</strong>{servicos}
            </div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=folium.Tooltip(
                f"{nome} ({tipo})",
                style="border-radius: 8px; font-family: sans-serif; font-size: 11px; padding: 4px 8px; background-color: #FFFFFF; color: #0F172A; border: 1px solid #CBD5E1;"
            ),
            icon=folium.Icon(color=cor_marcador, icon=icone, prefix="fa")
        ).add_to(fg_equipamentos)

    fg_equipamentos.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    return mapa
