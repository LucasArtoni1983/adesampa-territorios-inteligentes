"""
Testes automatizados para o módulo src/data_loader.py
Verifica a integridade e integridade referencial dos datasets da cidade de São Paulo.
"""

from src.data_loader import carregar_indicadores, carregar_equipamentos, carregar_geojson_distritos


def test_carregar_indicadores():
    df = carregar_indicadores()
    assert len(df) == 96, f"Esperado 96 distritos, encontrado {len(df)}"
    
    colunas_obrigatorias = [
        "distrito", "subprefeitura", "zona", "populacao",
        "renda_media_formal", "tempo_deslocamento_min",
        "empregos_por_100hab", "equipamentos_adesampa_ativos",
        "indice_deserto_fomento", "classificacao_vulnerabilidade"
    ]
    for col in colunas_obrigatorias:
        assert col in df.columns, f"Coluna obrigatória ausente: {col}"
    
    # Validação de integridade numérica
    assert df["populacao"].min() > 0
    assert df["renda_media_formal"].min() > 1000.0
    assert df["indice_deserto_fomento"].between(0.0, 10.0).all()


def test_carregar_equipamentos():
    equipamentos = carregar_equipamentos()
    assert len(equipamentos) >= 20, "Catálogo deve conter ao menos 20 unidades públicas da ADE SAMPA"

    for eq in equipamentos:
        assert "nome" in eq
        assert "tipo" in eq
        assert "latitude" in eq and "longitude" in eq
        assert -24.1 <= eq["latitude"] <= -23.3, f"Latitude fora dos limites de SP: {eq['latitude']}"
        assert -47.0 <= eq["longitude"] <= -46.3, f"Longitude fora dos limites de SP: {eq['longitude']}"


def test_carregar_geojson_distritos():
    geojson = carregar_geojson_distritos()
    assert geojson.get("type") == "FeatureCollection"
    features = geojson.get("features", [])
    assert len(features) == 96, f"GeoJSON deve conter 96 polígonos, encontrado {len(features)}"
    
    for f in features:
        props = f.get("properties", {})
        assert "nome" in props
        assert "indice_deserto" in props
        assert "cor" in props
