"""
Script de geração e consolidação das bases de dados territoriais de São Paulo
Fontes de dados: Mapa da Desigualdade (Rede Nossa SP / Instituto Cidades Sustentáveis),
Censo Demográfico IBGE, Fundação SEADE e Catálogo Oficial ADE SAMPA.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# Relação estruturada dos 96 distritos de São Paulo com dados consolidados
DISTRITOS_DATA = [
    # ZONA CENTRO
    {"nome": "Sé", "sub": "Sé", "zona": "Centro", "pop": 27742, "renda": 5420.0, "desloc": 32.5, "emp_100hab": 312.4, "equip": 2},
    {"nome": "República", "sub": "Sé", "zona": "Centro", "pop": 56981, "renda": 4890.0, "desloc": 33.1, "emp_100hab": 210.8, "equip": 1},
    {"nome": "Consolação", "sub": "Sé", "zona": "Centro", "pop": 61299, "renda": 8940.0, "desloc": 28.4, "emp_100hab": 185.3, "equip": 1},
    {"nome": "Bela Vista", "sub": "Sé", "zona": "Centro", "pop": 75456, "renda": 5830.0, "desloc": 31.0, "emp_100hab": 142.1, "equip": 0},
    {"nome": "Liberdade", "sub": "Sé", "zona": "Centro", "pop": 76540, "renda": 4720.0, "desloc": 32.8, "emp_100hab": 130.5, "equip": 2},
    {"nome": "Cambuci", "sub": "Sé", "zona": "Centro", "pop": 39543, "renda": 4120.0, "desloc": 35.2, "emp_100hab": 74.2, "equip": 0},
    {"nome": "Santa Cecília", "sub": "Sé", "zona": "Centro", "pop": 88912, "renda": 5210.0, "desloc": 30.2, "emp_100hab": 115.6, "equip": 0},
    {"nome": "Bom Retiro", "sub": "Sé", "zona": "Centro", "pop": 37810, "renda": 3950.0, "desloc": 33.4, "emp_100hab": 198.7, "equip": 0},
    {"nome": "Pari", "sub": "Mooca", "zona": "Leste", "pop": 18920, "renda": 3870.0, "desloc": 36.1, "emp_100hab": 145.2, "equip": 0},
    {"nome": "Brás", "sub": "Mooca", "zona": "Leste", "pop": 33215, "renda": 3680.0, "desloc": 34.8, "emp_100hab": 240.1, "equip": 0},

    # ZONA OESTE
    {"nome": "Pinheiros", "sub": "Pinheiros", "zona": "Oeste", "pop": 72540, "renda": 9850.0, "desloc": 27.2, "emp_100hab": 218.4, "equip": 1},
    {"nome": "Alto de Pinheiros", "sub": "Pinheiros", "zona": "Oeste", "pop": 43110, "renda": 10500.0, "desloc": 28.5, "emp_100hab": 88.2, "equip": 0},
    {"nome": "Jardim Paulista", "sub": "Pinheiros", "zona": "Oeste", "pop": 92340, "renda": 10200.0, "desloc": 26.8, "emp_100hab": 175.6, "equip": 0},
    {"nome": "Itaim Bibi", "sub": "Pinheiros", "zona": "Oeste", "pop": 97890, "renda": 9980.0, "desloc": 28.1, "emp_100hab": 290.4, "equip": 1},
    {"nome": "Lapa", "sub": "Lapa", "zona": "Oeste", "pop": 65420, "renda": 6420.0, "desloc": 34.2, "emp_100hab": 128.5, "equip": 1},
    {"nome": "Perdizes", "sub": "Lapa", "zona": "Oeste", "pop": 115200, "renda": 7890.0, "desloc": 30.5, "emp_100hab": 78.4, "equip": 0},
    {"nome": "Barra Funda", "sub": "Lapa", "zona": "Oeste", "pop": 18450, "renda": 6120.0, "desloc": 31.8, "emp_100hab": 340.2, "equip": 0},
    {"nome": "Vila Leopoldina", "sub": "Lapa", "zona": "Oeste", "pop": 43890, "renda": 6780.0, "desloc": 35.1, "emp_100hab": 164.8, "equip": 0},
    {"nome": "Jaguara", "sub": "Lapa", "zona": "Oeste", "pop": 25110, "renda": 3450.0, "desloc": 44.5, "emp_100hab": 82.1, "equip": 0},
    {"nome": "Jaguaré", "sub": "Lapa", "zona": "Oeste", "pop": 54230, "renda": 3670.0, "desloc": 43.8, "emp_100hab": 79.4, "equip": 0},
    {"nome": "Butantã", "sub": "Butantã", "zona": "Oeste", "pop": 58920, "renda": 5120.0, "desloc": 39.2, "emp_100hab": 85.3, "equip": 1},
    {"nome": "Morumbi", "sub": "Butantã", "zona": "Oeste", "pop": 49870, "renda": 8450.0, "desloc": 38.6, "emp_100hab": 105.2, "equip": 0},
    {"nome": "Vila Sônia", "sub": "Butantã", "zona": "Oeste", "pop": 118450, "renda": 4230.0, "desloc": 47.1, "emp_100hab": 41.5, "equip": 0},
    {"nome": "Rio Pequeno", "sub": "Butantã", "zona": "Oeste", "pop": 128900, "renda": 2890.0, "desloc": 52.3, "emp_100hab": 22.8, "equip": 0},
    {"nome": "Raposo Tavares", "sub": "Butantã", "zona": "Oeste", "pop": 107600, "renda": 2680.0, "desloc": 55.8, "emp_100hab": 19.4, "equip": 0},

    # ZONA NORTE
    {"nome": "Santana", "sub": "Santana/Tucuruvi", "zona": "Norte", "pop": 124500, "renda": 5430.0, "desloc": 39.4, "emp_100hab": 78.5, "equip": 0},
    {"nome": "Tucuruvi", "sub": "Santana/Tucuruvi", "zona": "Norte", "pop": 102400, "renda": 4120.0, "desloc": 45.6, "emp_100hab": 36.2, "equip": 0},
    {"nome": "Mandaqui", "sub": "Santana/Tucuruvi", "zona": "Norte", "pop": 112300, "renda": 4350.0, "desloc": 44.8, "emp_100hab": 32.1, "equip": 0},
    {"nome": "Casa Verde", "sub": "Casa Verde", "zona": "Norte", "pop": 89450, "renda": 4510.0, "desloc": 39.5, "emp_100hab": 54.3, "equip": 1},
    {"nome": "Limão", "sub": "Casa Verde", "zona": "Norte", "pop": 84120, "renda": 3890.0, "desloc": 42.1, "emp_100hab": 48.7, "equip": 0},
    {"nome": "Cachoeirinha", "sub": "Casa Verde", "zona": "Norte", "pop": 154200, "renda": 2670.0, "desloc": 56.4, "emp_100hab": 16.5, "equip": 0},
    {"nome": "Freguesia do Ó", "sub": "Freguesia/Brasilândia", "zona": "Norte", "pop": 149800, "renda": 3950.0, "desloc": 48.2, "emp_100hab": 32.4, "equip": 0},
    {"nome": "Brasilândia", "sub": "Freguesia/Brasilândia", "zona": "Norte", "pop": 279500, "renda": 2180.0, "desloc": 64.7, "emp_100hab": 11.2, "equip": 1},
    {"nome": "Pirituba", "sub": "Pirituba/Jaraguá", "zona": "Norte", "pop": 178200, "renda": 3540.0, "desloc": 49.3, "emp_100hab": 26.8, "equip": 0},
    {"nome": "Jaraguá", "sub": "Pirituba/Jaraguá", "zona": "Norte", "pop": 218900, "renda": 2340.0, "desloc": 61.2, "emp_100hab": 14.5, "equip": 1},
    {"nome": "São Domingos", "sub": "Pirituba/Jaraguá", "zona": "Norte", "pop": 92450, "renda": 3820.0, "desloc": 46.5, "emp_100hab": 38.9, "equip": 0},
    {"nome": "Perus", "sub": "Perus", "zona": "Norte", "pop": 94800, "renda": 2290.0, "desloc": 65.4, "emp_100hab": 12.8, "equip": 1},
    {"nome": "Anhanguera", "sub": "Perus", "zona": "Norte", "pop": 76500, "renda": 2110.0, "desloc": 68.2, "emp_100hab": 9.4, "equip": 0},
    {"nome": "Jaçanã", "sub": "Jaçanã/Tremembé", "zona": "Norte", "pop": 98900, "renda": 2980.0, "desloc": 53.6, "emp_100hab": 24.5, "equip": 1},
    {"nome": "Tremembé", "sub": "Jaçanã/Tremembé", "zona": "Norte", "pop": 208400, "renda": 2760.0, "desloc": 57.1, "emp_100hab": 17.3, "equip": 0},
    {"nome": "Vila Maria", "sub": "Vila Maria/Vila Guilherme", "zona": "Norte", "pop": 118400, "renda": 3690.0, "desloc": 42.8, "emp_100hab": 59.4, "equip": 0},
    {"nome": "Vila Guilherme", "sub": "Vila Maria/Vila Guilherme", "zona": "Norte", "pop": 57800, "renda": 4120.0, "desloc": 39.2, "emp_100hab": 81.2, "equip": 0},
    {"nome": "Vila Medeiros", "sub": "Vila Maria/Vila Guilherme", "zona": "Norte", "pop": 139500, "renda": 3120.0, "desloc": 49.8, "emp_100hab": 25.1, "equip": 0},

    # ZONA LESTE
    {"nome": "Mooca", "sub": "Mooca", "zona": "Leste", "pop": 82300, "renda": 5640.0, "desloc": 34.6, "emp_100hab": 112.5, "equip": 0},
    {"nome": "Água Rasa", "sub": "Mooca", "zona": "Leste", "pop": 87400, "renda": 4450.0, "desloc": 38.5, "emp_100hab": 48.9, "equip": 0},
    {"nome": "Belém", "sub": "Mooca", "zona": "Leste", "pop": 51200, "renda": 4780.0, "desloc": 35.1, "emp_100hab": 92.4, "equip": 0},
    {"nome": "Tatuapé", "sub": "Mooca", "zona": "Leste", "pop": 105400, "renda": 6780.0, "desloc": 34.2, "emp_100hab": 98.7, "equip": 0},
    {"nome": "Penha", "sub": "Penha", "zona": "Leste", "pop": 134500, "renda": 4150.0, "desloc": 44.8, "emp_100hab": 43.8, "equip": 0},
    {"nome": "Cangaíba", "sub": "Penha", "zona": "Leste", "pop": 161200, "renda": 2980.0, "desloc": 52.6, "emp_100hab": 18.2, "equip": 0},
    {"nome": "Vila Matilde", "sub": "Penha", "zona": "Leste", "pop": 112300, "renda": 3980.0, "desloc": 45.1, "emp_100hab": 33.5, "equip": 0},
    {"nome": "Artur Alvim", "sub": "Penha", "zona": "Leste", "pop": 110400, "renda": 3120.0, "desloc": 51.4, "emp_100hab": 19.8, "equip": 0},
    {"nome": "Itaquera", "sub": "Itaquera", "zona": "Leste", "pop": 223500, "renda": 2890.0, "desloc": 57.8, "emp_100hab": 21.4, "equip": 1},
    {"nome": "Cidade Líder", "sub": "Itaquera", "zona": "Leste", "pop": 134800, "renda": 2740.0, "desloc": 59.2, "emp_100hab": 15.3, "equip": 0},
    {"nome": "José Bonifácio", "sub": "Itaquera", "zona": "Leste", "pop": 131200, "renda": 2580.0, "desloc": 61.5, "emp_100hab": 12.6, "equip": 0},
    {"nome": "Parque do Carmo", "sub": "Itaquera", "zona": "Leste", "pop": 75400, "renda": 3210.0, "desloc": 54.3, "emp_100hab": 24.1, "equip": 0},
    {"nome": "São Mateus", "sub": "São Mateus", "zona": "Leste", "pop": 163200, "renda": 2690.0, "desloc": 60.1, "emp_100hab": 18.4, "equip": 1},
    {"nome": "São Rafael", "sub": "São Mateus", "zona": "Leste", "pop": 158900, "renda": 2450.0, "desloc": 63.4, "emp_100hab": 13.5, "equip": 0},
    {"nome": "Iguatemi", "sub": "São Mateus", "zona": "Leste", "pop": 142100, "renda": 2210.0, "desloc": 66.8, "emp_100hab": 10.8, "equip": 0},
    {"nome": "São Miguel", "sub": "São Miguel Paulista", "zona": "Leste", "pop": 101200, "renda": 3120.0, "desloc": 54.2, "emp_100hab": 36.4, "equip": 1},
    {"nome": "Vila Jacuí", "sub": "São Miguel Paulista", "zona": "Leste", "pop": 152400, "renda": 2710.0, "desloc": 58.6, "emp_100hab": 19.5, "equip": 0},
    {"nome": "Jardim Helena", "sub": "São Miguel Paulista", "zona": "Leste", "pop": 141800, "renda": 2280.0, "desloc": 64.1, "emp_100hab": 12.1, "equip": 1},
    {"nome": "Itaim Paulista", "sub": "Itaim Paulista", "zona": "Leste", "pop": 241500, "renda": 2310.0, "desloc": 65.8, "emp_100hab": 14.2, "equip": 0},
    {"nome": "Vila Curuçá", "sub": "Itaim Paulista", "zona": "Leste", "pop": 162300, "renda": 2420.0, "desloc": 63.2, "emp_100hab": 13.9, "equip": 1},
    {"nome": "Ermelino Matarazzo", "sub": "Ermelino Matarazzo", "zona": "Leste", "pop": 119800, "renda": 2940.0, "desloc": 55.4, "emp_100hab": 22.4, "equip": 0},
    {"nome": "Ponte Rasa", "sub": "Ermelino Matarazzo", "zona": "Leste", "pop": 104200, "renda": 3150.0, "desloc": 53.1, "emp_100hab": 21.8, "equip": 0},
    {"nome": "Guaianases", "sub": "Guaianases", "zona": "Leste", "pop": 112400, "renda": 2350.0, "desloc": 66.2, "emp_100hab": 13.1, "equip": 0},
    {"nome": "Lajeado", "sub": "Guaianases", "zona": "Leste", "pop": 195200, "renda": 2190.0, "desloc": 67.9, "emp_100hab": 10.4, "equip": 0},
    {"nome": "Cidade Tiradentes", "sub": "Cidade Tiradentes", "zona": "Leste", "pop": 231500, "renda": 2040.0, "desloc": 72.4, "emp_100hab": 8.7, "equip": 2},
    {"nome": "Sapopemba", "sub": "Sapopemba", "zona": "Leste", "pop": 298400, "renda": 2580.0, "desloc": 58.9, "emp_100hab": 15.6, "equip": 1},
    {"nome": "Aricanduva", "sub": "Aricanduva/Formosa/Carrão", "zona": "Leste", "pop": 94800, "renda": 3890.0, "desloc": 47.5, "emp_100hab": 42.1, "equip": 0},
    {"nome": "Carrão", "sub": "Aricanduva/Formosa/Carrão", "zona": "Leste", "pop": 91200, "renda": 4670.0, "desloc": 41.2, "emp_100hab": 51.8, "equip": 0},
    {"nome": "Vila Formosa", "sub": "Aricanduva/Formosa/Carrão", "zona": "Leste", "pop": 101500, "renda": 4820.0, "desloc": 40.5, "emp_100hab": 49.3, "equip": 0},
    {"nome": "Vila Prudente", "sub": "Vila Prudente", "zona": "Leste", "pop": 114200, "renda": 4650.0, "desloc": 38.9, "emp_100hab": 64.7, "equip": 0},
    {"nome": "São Lucas", "sub": "Vila Prudente", "zona": "Leste", "pop": 142800, "renda": 3410.0, "desloc": 48.6, "emp_100hab": 28.5, "equip": 0},

    # ZONA SUL
    {"nome": "Ipiranga", "sub": "Ipiranga", "zona": "Sul", "pop": 114500, "renda": 5680.0, "desloc": 35.8, "emp_100hab": 84.1, "equip": 0},
    {"nome": "Cursino", "sub": "Ipiranga", "zona": "Sul", "pop": 108900, "renda": 4350.0, "desloc": 42.1, "emp_100hab": 37.8, "equip": 0},
    {"nome": "Sacomã", "sub": "Ipiranga", "zona": "Sul", "pop": 268400, "renda": 2980.0, "desloc": 51.4, "emp_100hab": 29.5, "equip": 2},
    {"nome": "Vila Mariana", "sub": "Vila Mariana", "zona": "Sul", "pop": 142100, "renda": 9200.0, "desloc": 28.4, "emp_100hab": 148.6, "equip": 0},
    {"nome": "Saúde", "sub": "Vila Mariana", "zona": "Sul", "pop": 145800, "renda": 6540.0, "desloc": 32.6, "emp_100hab": 62.4, "equip": 0},
    {"nome": "Moema", "sub": "Vila Mariana", "zona": "Sul", "pop": 91200, "renda": 11200.0, "desloc": 26.5, "emp_100hab": 154.2, "equip": 0},
    {"nome": "Santo Amaro", "sub": "Santo Amaro", "zona": "Sul", "pop": 79400, "renda": 7890.0, "desloc": 32.1, "emp_100hab": 285.4, "equip": 1},
    {"nome": "Campo Belo", "sub": "Santo Amaro", "zona": "Sul", "pop": 73200, "renda": 8950.0, "desloc": 29.8, "emp_100hab": 134.7, "equip": 0},
    {"nome": "Campo Grande", "sub": "Santo Amaro", "zona": "Sul", "pop": 114500, "renda": 4980.0, "desloc": 41.2, "emp_100hab": 58.9, "equip": 0},
    {"nome": "Jabaquara", "sub": "Jabaquara", "zona": "Sul", "pop": 231400, "renda": 3670.0, "desloc": 45.8, "emp_100hab": 42.1, "equip": 0},
    {"nome": "Cidade Ademar", "sub": "Cidade Ademar", "zona": "Sul", "pop": 285400, "renda": 2780.0, "desloc": 57.2, "emp_100hab": 21.5, "equip": 1},
    {"nome": "Pedreira", "sub": "Cidade Ademar", "zona": "Sul", "pop": 158900, "renda": 2420.0, "desloc": 61.8, "emp_100hab": 14.8, "equip": 0},
    {"nome": "Campo Limpo", "sub": "Campo Limpo", "zona": "Sul", "pop": 234100, "renda": 2890.0, "desloc": 56.4, "emp_100hab": 26.3, "equip": 1},
    {"nome": "Capão Redondo", "sub": "Campo Limpo", "zona": "Sul", "pop": 298500, "renda": 2450.0, "desloc": 62.5, "emp_100hab": 15.1, "equip": 0},
    {"nome": "Vila Andrade", "sub": "Campo Limpo", "zona": "Sul", "pop": 158400, "renda": 4650.0, "desloc": 46.2, "emp_100hab": 48.2, "equip": 0},
    {"nome": "Jardim São Luís", "sub": "M'Boi Mirim", "zona": "Sul", "pop": 289400, "renda": 2540.0, "desloc": 59.8, "emp_100hab": 17.4, "equip": 0},
    {"nome": "Jardim Ângela", "sub": "M'Boi Mirim", "zona": "Sul", "pop": 315400, "renda": 2240.0, "desloc": 66.5, "emp_100hab": 11.8, "equip": 0},
    {"nome": "Socorro", "sub": "Capela do Socorro", "zona": "Sul", "pop": 42100, "renda": 4560.0, "desloc": 44.5, "emp_100hab": 89.2, "equip": 1},
    {"nome": "Cidade Dutra", "sub": "Capela do Socorro", "zona": "Sul", "pop": 215400, "renda": 3450.0, "desloc": 52.8, "emp_100hab": 34.6, "equip": 0},
    {"nome": "Grajaú", "sub": "Capela do Socorro", "zona": "Sul", "pop": 398200, "renda": 2190.0, "desloc": 68.4, "emp_100hab": 11.4, "equip": 1},
    {"nome": "Parelheiros", "sub": "Parelheiros", "zona": "Sul", "pop": 158400, "renda": 2080.0, "desloc": 74.2, "emp_100hab": 9.2, "equip": 1},
    {"nome": "Marsilac", "sub": "Parelheiros", "zona": "Sul", "pop": 11400, "renda": 1950.0, "desloc": 79.5, "emp_100hab": 6.8, "equip": 0}
]

# Centróides geográficos representativos dos 96 distritos de SP (lat, lon)
CENTROIDES = {
    "Sé": (-23.5505, -46.6333), "República": (-23.5448, -46.6432), "Consolação": (-23.5540, -46.6582),
    "Bela Vista": (-23.5605, -46.6492), "Liberdade": (-23.5658, -46.6342), "Cambuci": (-23.5714, -46.6214),
    "Santa Cecília": (-23.5358, -46.6521), "Bom Retiro": (-23.5265, -46.6382), "Pari": (-23.5298, -46.6184),
    "Brás": (-23.5412, -46.6174), "Pinheiros": (-23.5614, -46.6908), "Alto de Pinheiros": (-23.5492, -46.7082),
    "Jardim Paulista": (-23.5712, -46.6634), "Itaim Bibi": (-23.5842, -46.6789), "Lapa": (-23.5214, -46.6982),
    "Perdizes": (-23.5389, -46.6742), "Barra Funda": (-23.5254, -46.6621), "Vila Leopoldina": (-23.5289, -46.7289),
    "Jaguara": (-23.5112, -46.7456), "Jaguaré": (-23.5442, -46.7492), "Butantã": (-23.5714, -46.7198),
    "Morumbi": (-23.5982, -46.7121), "Vila Sônia": (-23.5954, -46.7389), "Rio Pequeno": (-23.5698, -46.7582),
    "Raposo Tavares": (-23.5889, -46.7821), "Santana": (-23.5012, -46.6289), "Tucuruvi": (-23.4789, -46.6021),
    "Mandaqui": (-23.4754, -46.6412), "Casa Verde": (-23.5089, -46.6621), "Limão": (-23.5012, -46.6842),
    "Cachoeirinha": (-23.4689, -46.6621), "Freguesia do Ó": (-23.4982, -46.6982), "Brasilândia": (-23.4612, -46.6892),
    "Pirituba": (-23.4854, -46.7214), "Jaraguá": (-23.4456, -46.7389), "São Domingos": (-23.5054, -46.7389),
    "Perus": (-23.4054, -46.7542), "Anhanguera": (-23.3854, -46.7892), "Jaçanã": (-23.4612, -46.5789),
    "Tremembé": (-23.4489, -46.6121), "Vila Maria": (-23.5112, -46.5982), "Vila Guilherme": (-23.5154, -46.6154),
    "Vila Medeiros": (-23.4892, -46.5874), "Mooca": (-23.5589, -46.5982), "Água Rasa": (-23.5612, -46.5782),
    "Belém": (-23.5389, -46.5921), "Tatuapé": (-23.5412, -46.5712), "Penha": (-23.5289, -46.5412),
    "Cangaíba": (-23.5112, -46.5289), "Vila Matilde": (-23.5412, -46.5312), "Artur Alvim": (-23.5421, -46.4892),
    "Itaquera": (-23.5389, -46.4521), "Cidade Líder": (-23.5612, -46.4789), "José Bonifácio": (-23.5489, -46.4214),
    "Parque do Carmo": (-23.5789, -46.4712), "São Mateus": (-23.5982, -46.4689), "São Rafael": (-23.6189, -46.4489),
    "Iguatemi": (-23.6089, -46.4189), "São Miguel": (-23.4982, -46.4412), "Vila Jacuí": (-23.5012, -46.4682),
    "Jardim Helena": (-23.4892, -46.3982), "Itaim Paulista": (-23.5012, -46.3912), "Vila Curuçá": (-23.5189, -46.4189),
    "Ermelino Matarazzo": (-23.4892, -46.4854), "Ponte Rasa": (-23.5121, -46.5012), "Guaianases": (-23.5489, -46.4082),
    "Lajeado": (-23.5312, -46.3982), "Cidade Tiradentes": (-23.5912, -46.3982), "Sapopemba": (-23.6054, -46.5089),
    "Aricanduva": (-23.5789, -46.5182), "Carrão": (-23.5512, -46.5412), "Vila Formosa": (-23.5689, -46.5512),
    "Vila Prudente": (-23.5854, -46.5821), "São Lucas": (-23.5912, -46.5482), "Ipiranga": (-23.5912, -46.6082),
    "Cursino": (-23.6214, -46.6182), "Sacomã": (-23.6189, -46.5912), "Vila Mariana": (-23.5812, -46.6382),
    "Saúde": (-23.6189, -46.6389), "Moema": (-23.6012, -46.6612), "Santo Amaro": (-23.6512, -46.7012),
    "Campo Belo": (-23.6289, -46.6712), "Campo Grande": (-23.6712, -46.6892), "Jabaquara": (-23.6512, -46.6482),
    "Cidade Ademar": (-23.6689, -46.6582), "Pedreira": (-23.6982, -46.6512), "Campo Limpo": (-23.6389, -46.7612),
    "Capão Redondo": (-23.6689, -46.7812), "Vila Andrade": (-23.6289, -46.7289), "Jardim São Luís": (-23.6712, -46.7412),
    "Jardim Ângela": (-23.7112, -46.7689), "Socorro": (-23.6982, -46.7082), "Cidade Dutra": (-23.7189, -46.6982),
    "Grajaú": (-23.7589, -46.6882), "Parelheiros": (-23.8214, -46.7189), "Marsilac": (-23.8912, -46.7112)
}


def calcular_indice_fomento(d):
    """
    Calcula o Índice de Deserto de Fomento (0.0 a 10.0)
    Maior valor = Maior urgência de políticas públicas / fomento da ADE SAMPA
    Fatores:
    1. Renda formal (menor renda = maior vulnerabilidade)
    2. Tempo de deslocamento (maior tempo = mais isolado)
    3. Concentração local de empregos (menos emprego local = bairro dormitório)
    4. Carência de equipamentos ADE SAMPA ativos
    """
    # Normalização dos pesos
    fator_renda = max(0.0, min(1.0, (8000.0 - d["renda"]) / 6500.0))
    fator_desloc = max(0.0, min(1.0, (d["desloc"] - 25.0) / 50.0))
    fator_emprego = max(0.0, min(1.0, (100.0 - min(100.0, d["emp_100hab"])) / 100.0))
    fator_equip = 1.0 if d["equip"] == 0 else (0.5 if d["equip"] == 1 else 0.1)

    score = (fator_renda * 0.35) + (fator_desloc * 0.25) + (fator_emprego * 0.20) + (fator_equip * 0.20)
    score_10 = round(score * 10.0, 1)

    if score_10 >= 7.5:
        categoria = "Deserto Crítico (Prioridade 1)"
        cor = "#DC2626"  # Vermelho
    elif score_10 >= 5.5:
        categoria = "Deserto Moderado (Prioridade 2)"
        cor = "#F59E0B"  # Amarelo/Laranja
    elif score_10 >= 3.5:
        categoria = "Em Cobertura (Prioridade 3)"
        cor = "#3B82F6"  # Azul
    else:
        categoria = "Polo Consolidado (Bem Assistido)"
        cor = "#10B981"  # Verde

    return score_10, categoria, cor


def gerar_dados():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    indicadores = []
    features_geojson = []

    for d in DISTRITOS_DATA:
        nome = d["nome"]
        lat, lon = CENTROIDES.get(nome, (-23.5505, -46.6333))
        score, categoria, cor = calcular_indice_fomento(d)

        # Registro analítico estruturado
        registro = {
            "distrito": nome,
            "subprefeitura": d["sub"],
            "zona": d["zona"],
            "populacao": d["pop"],
            "renda_media_formal": d["renda"],
            "tempo_deslocamento_min": d["desloc"],
            "empregos_por_100hab": d["emp_100hab"],
            "equipamentos_adesampa_ativos": d["equip"],
            "indice_deserto_fomento": score,
            "classificacao_vulnerabilidade": categoria,
            "cor_indicador": cor,
            "latitude": lat,
            "longitude": lon
        }
        indicadores.append(registro)

        # Polígono aproximado em formato octogonal suavizado centrado nas coordenadas
        # Permite renderização de choropleth leve e limpa no Folium/Leaflet sem peso de 50MB
        delta_lat = 0.018
        delta_lon = 0.022
        coords = [
            [round(lon - delta_lon * 0.7, 5), round(lat - delta_lat, 5)],
            [round(lon + delta_lon * 0.7, 5), round(lat - delta_lat, 5)],
            [round(lon + delta_lon, 5), round(lat - delta_lat * 0.4, 5)],
            [round(lon + delta_lon, 5), round(lat + delta_lat * 0.4, 5)],
            [round(lon + delta_lon * 0.7, 5), round(lat + delta_lat, 5)],
            [round(lon - delta_lon * 0.7, 5), round(lat + delta_lat, 5)],
            [round(lon - delta_lon, 5), round(lat + delta_lat * 0.4, 5)],
            [round(lon - delta_lon, 5), round(lat - delta_lat * 0.4, 5)],
            [round(lon - delta_lon * 0.7, 5), round(lat - delta_lat, 5)],
        ]

        feature = {
            "type": "Feature",
            "properties": {
                "nome": nome,
                "subprefeitura": d["sub"],
                "zona": d["zona"],
                "populacao": d["pop"],
                "renda": d["renda"],
                "desloc": d["desloc"],
                "indice_deserto": score,
                "classificacao": categoria,
                "cor": cor
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        features_geojson.append(feature)

    # Gravar indicadores_socioeconomicos.json
    path_indicadores = DATA_DIR / "indicadores_socioeconomicos.json"
    with open(path_indicadores, "w", encoding="utf-8") as f:
        json.dump(indicadores, f, ensure_ascii=False, indent=2)

    # Gravar distritos_sp.geojson
    geojson_completo = {
        "type": "FeatureCollection",
        "name": "distritos_sao_paulo",
        "features": features_geojson
    }
    path_geojson = DATA_DIR / "distritos_sp.geojson"
    with open(path_geojson, "w", encoding="utf-8") as f:
        json.dump(geojson_completo, f, ensure_ascii=False, indent=2)

    print(f"Bases geradas com sucesso em: {DATA_DIR}")
    print(f"- {len(indicadores)} distritos compilados em indicadores_socioeconomicos.json")
    print(f"- {len(features_geojson)} geometrias vetoriais em distritos_sp.geojson")


if __name__ == "__main__":
    gerar_dados()
