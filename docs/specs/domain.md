# Ade Sampa — domain.md

## Linguagem ubíqua

- **ADE SAMPA**: Agência São Paulo de Desenvolvimento, voltada ao fomento do empreendedorismo, inovação e desenvolvimento econômico na capital paulista.
- **GeoSampa**: Mapa digital oficial da cidade de São Paulo com camadas georreferenciadas de equipamentos públicos, zoneamento, demografia e infraestrutura.
- **Portal de Dados Abertos**: Repositório central de bases e indicadores dos órgãos municipais de São Paulo.
- **Indicador Municipal**: Métrica de desempenho, cobertura social, saúde, mobilidade ou infraestrutura pública.
- **Equipamento Público**: Ponto de atendimento ou serviço municipal (postos de atendimento, escolas, UBS, polos culturais, etc.).

## Entidades e agregados

### Indicador / Dado Municipal
Atributos principais:
- id
- regiao / subprefeitura / distrito
- valor / métrica
- dataReferencia
- fonteOrigem

### Equipamento / Serviço
Atributos principais:
- id
- nome
- categoria / tipo
- coordenadas (latitude, longitude)
- endereco
- statusFuncionamento

## Políticas de dados

- Bases utilizadas são públicas e abertas (Prefeitura de SP, IBGE, DataSUS, etc.).
- Não há coleta de dados pessoais sensíveis sem necessidade estrita.
- Em caso de dados simulados ou sintéticos, devem ser claramente indicados conforme o edital.
