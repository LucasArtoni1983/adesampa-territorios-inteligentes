# 🌐 ADE SAMPA Territórios Inteligentes
### Painel Integrado de Diagnóstico Territorial, Cobertura de Equipamentos e Fomento ao Empreendedorismo Periférico

[![Edital](https://img.shields.io/badge/ADE%20SAMPA-Edital%20005%2F2026-blue)](https://adesampa.com.br/)
[![Cargo](https://img.shields.io/badge/Cargo-Assistente%20II%20--%20Dados%20e%20IA-success)](#)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-blue.svg?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)
[![Testes](https://img.shields.io/badge/Testes-18%20passing-brightgreen.svg?logo=pytest)](https://docs.pytest.org/)
[![Acessibilidade](https://img.shields.io/badge/WCAG%202.1-AA%20Compliant-brightgreen)](https://www.w3.org/WAI/standards-guidelines/wcag/)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green)](#)

---

## 📑 Sumário

- [1. Título e Visão Geral](#1-título-e-visão-geral)
- [🗺️ Mapa do Site & Guia do Usuário (SITEMAP.md)](SITEMAP.md)
- [2. Descrição do Problema Identificado](#2-descrição-do-problema-identificado)
- [3. Contexto e Justificativa da Escolha](#3-contexto-e-justificativa-da-escolha)
- [4. Órgão, Secretaria e Políticas Públicas Vinculadas](#4-órgão-secretaria-e-políticas-públicas-vinculadas)
- [5. Descrição da Solução Desenvolvida](#5-descrição-da-solução-desenvolvida)
- [6. Público-Alvo e Gestão Municipal Beneficiada](#6-público-alvo-e-gestão-municipal-beneficiada)
- [7. Principais Funcionalidades](#7-principais-funcionalidades)
- [8. Fontes Pesquisadas e Dados Utilizados](#8-fontes-pesquisadas-e-dados-utilizados)
- [9. Indicação de Dados Sintéticos ou Simulados](#9-indicação-de-dados-sintéticos-ou-simulados)
- [10. Justificativa das Principais Escolhas Realizadas](#10-justificativa-das-principais-escolhas-realizadas)
- [11. Metodologia Adotada](#11-metodologia-adotada)
- [12. Tecnologias, Bibliotecas e Plataformas Utilizadas](#12-tecnologias-bibliotecas-e-plataformas-utilizadas)
- [13. Utilização de Inteligência Artificial e Vibe Coding](#13-utilização-de-inteligência-artificial-e-vibe-coding)
- [14. Limitações Identificadas](#14-limitações-identificadas)
- [15. Possíveis Melhorias e Evoluções Futuras](#15-possíveis-melhorias-e-evoluções-futuras)
- [16. Instruções Completas para Execução (Banca Avaliadora)](#16-instruções-completas-para-execução-banca-avaliadora)

---

## 1. Título e Visão Geral

**ADE SAMPA Territórios Inteligentes** é uma aplicação web funcional com visualização geoespacial interativa e camada de inteligência analítica baseada em IA. A plataforma visa apoiar a **ADE SAMPA (Agência São Paulo de Desenvolvimento)** na identificação de "desertos de fomento produtivo", no planejamento territorial da expansão de suas unidades físicas (*Rede Teia*, *FabLabs Livres* e *Postos de Atendimento*) e no direcionamento inteligente de microcrédito e capacitação para os 96 distritos da capital paulista.

> 🗺️ **Guia do Usuário & Mapa do Site:** Para um roteiro guiado tela a tela, arquitetura de fluxos e roteiro expresso de 5 minutos para a banca avaliadora, consulte o documento **[SITEMAP.md](SITEMAP.md)** ou baixe o documento oficial ilustrado **[mapa_do_site_adesampa.pdf](docs/mapa_do_site_adesampa.pdf)** com capturas de tela fidedignas da aplicação.

---

## 2. Descrição do Problema Identificado

A cidade de São Paulo apresenta uma disparidade socioeconômica estrutural e histórica:
- **Concentração de Oportunidades:** Postos de trabalho formal, incubadoras e crédito produtivo concentram-se no centro expandido e no vetor sudoeste (Consolação, Pinheiros, Itaim Bibi).
- **Sobrevivência nas Periferias:** Em distritos periféricos populosos (como Brasilândia, Cidade Tiradentes, Parelheiros e Perus), a atividade empreendedora dá-se primariamente por necessidade, em condições de informalidade, carência de infraestrutura física e barreiras de acesso ao crédito.
- **Deslocamento Crônico:** Moradores de distritos periféricos perdem rotineiramente mais de 1 hora por trecho para acessar clientes ou serviços no centro, esvaziando a economia local.
- **Gargalo de Planejamento Público:** A gestão pública carece de uma visão integrada e georreferenciada que cruze indicadores do *Mapa da Desigualdade* com a localização exata dos equipamentos municipais de desenvolvimento econômico para identificar lacunas territoriais de cobertura.

---

## 3. Contexto e Justificativa da Escolha

O projeto foi concebido sob medida para o **Edital de Seleção Pública nº 005/2026** para a função de **Assistente II - Dados e IA da ADE SAMPA**. 

A escolha do tema decorre de:
1. **Aderência Direta à Missão Institucional:** A ADE SAMPA tem por objetivo estatutário fomentar a geração de emprego, renda e novos negócios, priorizando regiões de alta vulnerabilidade social.
2. **Dados Oficiais Abundantes:** Integração com bases abertas e cartográficas municipais reais ([GeoSampa](http://geosampa.prefeitura.sp.gov.br/) e Portal de Dados Abertos da PMSP).
3. **Uso Relevante e Ético de IA:** Aplicação da IA como ferramenta de auxílio à tomada de decisão pública, sintetizando dados complexos e sugerindo prioridades de ação governamental com base em evidências.

---

## 4. Órgão, Secretaria e Políticas Públicas Vinculadas

- **Órgão Principal:** ADE SAMPA — Agência São Paulo de Desenvolvimento.
- **Secretaria Municipal:** SMDET — Secretaria Municipal de Desenvolvimento Econômico e Trabalho da Prefeitura de São Paulo.
- **Políticas e Programas Relacionados:**
  - **Rede Teia:** Coworkings públicos e gratuitos instalados em bairros periféricos.
  - **FabLabs Livres SP:** Rede de laboratórios públicos de fabricação digital.
  - **CRED SAMPA & Banco do Povo:** Linhas de microcrédito e fundo municipal garantidor de aval.
  - **Fábrica de Negócios & Sampa Cast:** Programas de formação empreendedora e produção de conteúdo digital local.
  - **Plano de Metas da Cidade de São Paulo:** Metas de descentralização econômica e geração de renda nas periferias.

---

## 5. Descrição da Solução Desenvolvida

A solução é composta por:
1. **Módulo de Mapeamento Geográfico Interativo:** Renderização cartográfica vetorial dos 96 distritos de SP categorizados por níveis de carência econômica, com plotagem dos equipamentos da ADE SAMPA e buffers de raio de cobertura.
2. **Painel Analítico de Indicadores Distritais:** Interface comparativa com métricas de renda, emprego formal, tempo de deslocamento e densidade empreendedora.
3. **Módulo de Inteligência Artificial para Gestão:** Copiloto analítico que processa o perfil do distrito selecionado e gera um diagnóstico instantâneo recomendando alocação de programas (ex.: turmas prioritárias de microcrédito, unidades volantes ou expansão da Rede Teia).

---

## 6. Público-Alvo e Gestão Municipal Beneficiada

- **Técnicos e Analistas da ADE SAMPA / SMDET:** Para planejamento territorial de expansão de programas e prestação de contas.
- **Subprefeituras e Gestores Locais:** Para diagnóstico rápido das demandas de desenvolvimento econômico de cada região.
- **Cidadãos e Empreendedores Paulistanos:** Para consulta fácil dos equipamentos e serviços públicos disponíveis próximos à sua residência.

---

## 7. Principais Funcionalidades

- [x] **Mapa Territorial Interativo com Sincronização Dinâmica:** Realce automático dos distritos filtrados na barra lateral com auto-zoom aos limites da seleção (`fit_bounds`).
- [x] **Legenda Visual Intuitiva de Equipamentos:** Cartões explicativos com identificação iconográfica (💻 Rede Teia, 🧊 FabLab Livre, 💼 Posto ADE SAMPA, ⭕ Raio de 2.5 km e 🎙️ Estúdios Sampa Cast).
- [x] **Studio Dinâmico de Gráficos:** Construtor livre de gráficos com 7 estilos visuais (Linhas, Barras Horizontais, Barras Verticais, Pirulito/Lollipop, Área, Pizza e Dispersão).
- [x] **Ordenação Inteligente e Adaptativa:** Sentido ascendente/decrescente ativo nos gráficos de ranking e desabilitado com aviso explicativo nos gráficos de composição (Pizza) e plano cartesiano (Dispersão).
- [x] **Exportação de Gráficos em PNG de Alta Resolução:** Botão dedicado sob demanda para download de imagens em 300 DPI equivalente (1200x650px a 2x DPI) em todos os gráficos do Observatório.
- [x] **Exportação Tabular em CSV para Excel:** Download estruturado com codificação `UTF-8 com BOM` e delimitador `;` na barra lateral, no mapa e nos gráficos.
- [x] **Copiloto de IA e Diagnóstico Territorial:** Geração automatizada de parecer técnico com gargalos prioritários, plano de ação e download em Markdown.
- [x] **Catálogo Completo de Equipamentos ADE SAMPA:** Consulta de endereços, horários de funcionamento, bairros atendidos e filtro de estúdios Sampa Cast.
- [x] **Acessibilidade Digital (WCAG 2.1 AA):** Cartões de KPI com descrições semânticas em texto (*alt-text*), contrastes verificados e navegação por teclado.
- [x] **Auditoria de Qualidade e Testes:** 18 testes automatizados no `pytest` cobrindo integridade de dados, integridade de mapa, métricas e exportação PNG.

---

## 8. Fontes Pesquisadas e Dados Utilizados

- **[GeoSampa (Prefeitura de São Paulo)](https://geosampa.prefeitura.sp.gov.br/):** Malha cartográfica vetorial dos 96 distritos, limites de subprefeituras e equipamentos públicos municipais.
- **[Portal de Dados Abertos da PMSP](https://dados.prefeitura.sp.gov.br/):** Relação oficial de endereços e coordenadas dos espaços *Teia*, *FabLabs Livres* e postos de atendimento da ADE SAMPA.
- **[Mapa da Desigualdade (Rede Nossa São Paulo / Instituto Cidades Sustentáveis)](https://www.nossasaopaulo.org.br/):** Indicadores distritais de remuneração média, oferta de empregos formais e tempo de deslocamento.
- **[IBGE (Censo Demográfico)](https://censo2022.ibge.gov.br/) & [Fundação SEADE](https://repositorio.seade.gov.br/):** Dados populacionais consolidados e projeções socioeconômicas por distrito da capital.
- **[Portal Oficial da ADE SAMPA](https://adesampa.com.br/):** Programas, serviços e diretrizes de desenvolvimento econômico local.

---

## 9. Indicação de Dados Sintéticos ou Simulados

Em cumprimento ao item de **Utilização de Dados** do Edital nº 005/2026:
- **Dados Reais Utilizados:**
  - Localização, endereços e tipologia das unidades da *Rede Teia*, *FabLabs Livres* e postos *ADE SAMPA* (Portal de Dados Abertos da PMSP).
  - População distrital consolidada (IBGE / SEADE).
  - Remuneração média e tempo de deslocamento por distrito (Mapa da Desigualdade).
- **Métrica Analítica / Sintética Complementar:**
  - Para apoiar o módulo de IA na tomada de decisão, foi formulado o **Índice de Deserto de Fomento (IDF)**, variando de `0.0` (plenamente assistido) a `10.0` (deserto crítico de fomento produtivo).
  - **Fórmula e Premissas Matemáticas:**
    $$\text{IDF} = \left( 0.35 \times F_{\text{renda}} + 0.25 \times F_{\text{deslocamento}} + 0.20 \times F_{\text{emprego\_local}} + 0.20 \times F_{\text{carencia\_equipamento}} \right) \times 10$$
    * **$F_{\text{renda}}$:** Distância proporcional à remuneração de referência municipal (R$ 8.000,00).
    * **$F_{\text{deslocamento}}$:** Penalidade escalonada para distritos cujo tempo médio até o trabalho excede 45 minutos.
    * **$F_{\text{emprego\_local}}$:** Relação inversa à oferta de postos de trabalho formais dentro do próprio distrito.
    * **$F_{\text{carencia\_equipamento}}$:** Peso máximo (1.0) para distritos com 0 equipamentos públicos de desenvolvimento econômico da ADE SAMPA instalados.

---

## 10. Justificativa das Principais Escolhas Realizadas

1. **Python como Linguagem Central:** A escolha decorre do alinhamento direto com o cargo de **Assistente II - Dados e IA**. Python é o padrão da indústria para tratamento analítico, bibliotecas geoespaciais e inteligência artificial.
2. **Streamlit para a Aplicação Web:**
   * **Execução Ágil e Confiável pela Banca:** Dispensa configurações complexas de múltiplos servidores ou orquestradores de containers que frequentemente causam erros em máquinas de avaliação. Instalação e execução com 2 comandos diretos.
   * **Deploy Web Direto (Sem Docker):** Permite hospedagem gratuita no *Streamlit Community Cloud*, fornecendo um link público acessível por qualquer navegador.
   * **Ecossistema Nativo de Dados:** Integração transparente com bibliotecas como Folium, Pydeck, Plotly e Pandas.
3. **Formato dos Dados (GeoJSON e JSON estruturado em `data/`):**
   * Garante autonomia total (**zero dependência de APIs externas pagas ou instáveis** durante a avaliação da banca).
   * Arquivo cartográfico vetorizado de forma otimizada para carregamento leve e fluido.
4. **Módulo de IA Híbrido (Analítico + Generativo):**
   * Diagnóstico territorial baseado em regras analíticas robustas (garantindo confiabilidade estatística) complementado por síntese de texto orientada à tomada de decisão pública.

---

## 11. Metodologia Adotada

- **Spec-Driven Development (SDD):** Todas as etapas partem de especificações técnicas em `docs/specs/`.
- **Research → Plan → Implement → Verify → Review (RPI):** Ciclo rigoroso com validações prévias de dados e arquitetura.
- **Vibe Coding Orientado e Assistido por Agentes Especializados:** Uso orquestrado de sub-agents dedicados a segurança, dados, frontend e acessibilidade.

---

## 12. Tecnologias, Bibliotecas e Plataformas Utilizadas

- **Linguagem:** Python 3.12+ (compatível com 3.14)
- **Framework Web / Dashboard:** Streamlit
- **Visualização Geoespacial / Cartografia:** Folium / Streamlit-Folium
- **Gráficos e Indicadores Interativos:** Plotly Express
- **Manipulação e Engenharia de Dados:** Pandas / GeoPandas (ou Shapely/JSON)
- **Módulo de IA:** Assistente analítico e gerador de diretrizes de políticas públicas
- **Testes Automatizados:** Pytest
- **Padronização e Qualidade de Código:** Ruff / Black / Flake8

---

## 13. Utilização de Inteligência Artificial e Vibe Coding

Em estrito cumprimento às exigências do Edital de Seleção Pública nº 005/2026, esta seção documenta a metodologia de desenvolvimento assistido por Inteligência Artificial (Vibe Coding orientado a engenharia de software), detalhando as ferramentas adotadas, as etapas de aplicação, a atuação dos agentes especializados e o processo rigoroso de validação e ajuste dos resultados.

### 13.1. Ferramentas e Ambientes de IA Utilizados

O desenvolvimento combinou plataformas de raciocínio avançado, orquestração de código e automação de qualidade:

1. **Antigravity IDE & Gemini:** Ambiente de desenvolvimento agêntico integrado, utilizado para exploração do repositório, refatoração de código com consciência contextual ampla, automação de testes contínuos e instrumentação visual de interface.
2. **Claude Code (Anthropic):** Utilizado para síntese técnica, estruturação de fluxos lógicos e redação dos pareceres de políticas públicas do copiloto analítico.
3. **Playwright & Microsoft Edge Headless:** Ferramenta de automação de navegador operada por IA para captura fidedigna de telas da aplicação ativa em tempo de execução para geração do guia visual.
4. **ReportLab & Kaleido Engine:** Bibliotecas automatizadas para renderização programática de documentos institucionais em PDF (A4) e conversão de figuras Plotly interativas em imagens PNG de alta resolução (300 DPI).

---

### 13.2. Agentes Empregados e Etapas de Atuação

O ciclo de desenvolvimento seguiu o fluxo estruturado **Research → Plan → Implement → Verify → Review**. Para cada fase, agentes especializados foram acionados para funções estritas e especializadas:

| Agente | Finalidade Específica | Etapa do Desenvolvimento |
| :--- | :--- | :--- |
| **`researcher`** | Mapeamento e consolidação das bases de dados abertos da Prefeitura de São Paulo (GeoSampa, Dados Abertos, Fundação SEADE, Censo Demográfico) e levantamento do catálogo de programas da ADE SAMPA (*Rede Teia*, *FabLabs Livres*, *Sampa Cast*, *CRED SAMPA*, *Fábrica de Negócios*). | **Fase 1 — Pesquisa & Descoberta:** Coleta de evidências territoriais e compreensão dos 96 distritos paulistanos. |
| **`architect`** | Elaboração da arquitetura modular do sistema (camadas independentes de ingestão, cálculo de métricas, cartografia e interface), definição da formulação matemática do **Índice de Deserto de Fomento (IDF)** e registro das decisões de projeto em ADRs. | **Fase 2 — Planejamento & Arquitetura:** Especificação dos contratos de dados e desacoplamento de responsabilidades. |
| **`database` & `backend`** | Implementação das rotinas de carregamento de GeoJSON e CSVs, sanitização de campos numéricos, cálculo ponderado do IDF (0 a 10), filtros combinados de alta performance em memória e regras de negócio do motor analítico do copiloto. | **Fase 3 — Engenharia de Dados & Backend:** Construção dos módulos `data_loader.py` e `metrics_analyzer.py`. |
| **`frontend`** | Construção da interface interativa em Streamlit, integração dos mapas cartográficos com Folium (camadas cloropléticas, buffers de 2.5 km e auto-zoom dinâmico `fit_bounds`), e desenvolvimento do **Studio Dinâmico de 7 Gráficos** com Plotly. | **Fase 4 — Interface do Usuário (UI/UX):** Criação de `app.py`, design system responsivo e catálogo iconográfico institucional. |
| **`accessibility-reviewer`** | Auditoria e adequação da aplicação às normas **WCAG 2.1 nível AA**, garantindo contraste cromático superior a 4.5:1, foco navegável por teclado, descrições textuais alternativas (*alt-text*) e atributos `aria-label` em todos os cartões de indicadores e gráficos. | **Fase 5 — Acessibilidade Digital & Inclusão:** Revisão da interface visual e enriquecimento semântico do código HTML/CSS. |
| **`security-reviewer` & `code-reviewer`** | Verificação de conformidade com boas práticas de segurança defensiva: sanitização rigorosa de nomes de arquivos para exportação (`re.sub` contra injeção e path traversal), codificação `utf-8-sig` para integridade no Excel, proteção contra vazamento de stacktraces e conformidade com princípios SOLID e Clean Code. | **Fase 6 — Segurança Defensiva & Qualidade:** Auditoria de vulnerabilidades e refatoração de código limpo. |
| **`test-engineer`** | Criação e execução da suíte de testes automatizados com Pytest, cobrindo integridade cartográfica, consistência de cálculo do IDF, ordenação adaptativa de gráficos e resiliência offline. | **Fase 7 — Testes Automatizados & QA:** Implementação e validação de 18 testes unitários e de integração (100% passing). |
| **`devops` & `documentation-writer`** | Configuração dos scripts autossuficientes de execução com 1 clique (`run.bat` e `run.sh`), redação do README completo, elaboração do documento de navegação (`SITEMAP.md`) e compilação do guia visual ilustrado em PDF. | **Fase 8 — Automação de Ambiente & Entrega:** Garantia de autonomia total para a banca avaliadora. |

---

### 13.3. Avaliação, Ajuste e Incorporação dos Resultados à Solução

Nenhuma saída gerada por inteligência artificial foi incorporada sem supervisão crítica (*Human-in-the-Loop*). O processo de validação, refinamento e aceitação seguiu os seguintes critérios:

1. **Calibração Estatística da Metodologia do IDF:**
   - *Avaliação Inicial:* A formulação inicial proposta pela IA atribuía pesos idênticos (25% para cada dimensão) a todas as variáveis, o que gerava distorções em distritos centrais densos com tempo de trânsito intermediário.
   - *Ajuste e Incorporação:* Os pesos foram calibrados manualmente para refletir a realidade das políticas da ADE SAMPA: Vulnerabilidade de Renda (35%), Isolamento de Deslocamento (25%), Densidade Local de Empregos (20%) e Ausência de Equipamentos Ativos (20%). O cálculo foi validado contra os dados empíricos do *Mapa da Desigualdade*.

2. **Refinamento Cartográfico e Integridade Geoespacial:**
   - *Avaliação Inicial:* O componente de mapas proposto inicialmente apresentava dificuldades de enquadramento ao alternar filtros de subprefeituras periféricas e não suavizava visualmente os distritos fora do escopo selecionado.
   - *Ajuste e Incorporação:* Foi implementada rotina matemática em Python que calcula a caixa delimitadora (*bounding box*) exata das geometrias filtradas e executa o `fit_bounds` no Folium, aplicando opacidade reduzida e contorno pontilhado aos distritos não selecionados. As coordenadas geográficas de cada equipamento foram auditadas individualmente com os dados abertos da Prefeitura.

3. **Segurança e Compatibilidade na Exportação de Arquivos:**
   - *Avaliação Inicial:* A geração de downloads CSV utilizava a codificação padrão `utf-8`, que causa falhas de exibição de caracteres acentuados (cedilha, tis) ao ser aberta diretamente no Microsoft Excel em língua portuguesa.
   - *Ajuste e Incorporação:* O pipeline de exportação foi reescrito para utilizar `utf-8-sig` (com BOM) e delimitador de ponto-e-vírgula (`;`). Os nomes de arquivos gerados foram protegidos com expressões regulares para expurgar caracteres especiais, e a exportação gráfica em PNG foi integrada via motor Kaleido em resolução de impressão (300 DPI).

4. **Autonomia Operacional 100% Offline (Resiliência para a Banca):**
   - *Avaliação Inicial:* Modelos de IA frequentemente sugerem chamadas a APIs em nuvem pagas (como OpenAI, Google Gemini API ou Mapbox) para geração de texto ou camadas de azulejos de mapa, o que violaria a autonomia da banca avaliadora e criaria risco de falha por indisponibilidade de rede ou expiração de cotas.
   - *Ajuste e Incorporação:* A arquitetura foi adaptada para rodar de forma **completamente autônoma e local**. O copiloto de IA conta com um motor heurístico e analítico integrado que formula pareceres técnicos instantâneos sem depender de chaves de API externas. Foi adicionada ainda uma verificação rápida de conectividade via socket DNS (timeout de 0.8s) com indicador visual de status na barra lateral, garantindo funcionamento ininterrupto mesmo sem acesso à internet.

5. **Critério Rígido de Aceitação por Testes Automatizados:**
   - *Mecanismo de Controle:* Nenhuma modificação sugerida pela IA foi consolidada no código-fonte sem a prévia execução e aprovação de 100% da suíte de testes automatizados (`pytest`). Todos os 18 testes unitários e de integração foram mantidos verdes ao longo de todo o desenvolvimento.

---

## 14. Limitações Identificadas

Em conformidade com a postura de transparência exigida pelo edital:
1. **Nível de Agregação Espacial:** Os dados socioeconômicos e demográficos estão consolidados no nível dos **96 distritos municipais**. Variações intramunicipais microterritoriais (entre favelas, comunidades ou bairros dentro de um mesmo distrito amplo) não são individualizadas nesta versão.
2. **Periodicidade das Bases:** Indicadores do *Censo Demográfico* e do *Mapa da Desigualdade* possuem ciclos anuais ou decenais de atualização, refletindo a foto histórica oficial mais recente disponibilizada pelos órgãos de pesquisa.
3. **Modelagem de Cobertura Euclidiana:** O raio de cobertura adotado (2.5 km ao redor de cada unidade Teia e FabLab) é um buffer circular aproximado, servindo como estimativa visual de desassistência sem calcular a malha viária curva a curva de pedestres.

---

## 15. Possíveis Melhorias e Evoluções Futuras

1. **Isócronas Reais de Transporte Público (GTFS/SPTrans):** Substituir o raio euclidiano pelo cálculo de rotas reais a pé e por ônibus/metrô utilizando a API de dados abertos da SPTrans (Olho Vivo).
2. **Conexão Direta WFS/WMS com o GeoSampa:** Implementar ingestão automatizada e sincronizada com as camadas cartográficas dinâmicas da Prefeitura de SP.
3. **Chat Conversacional com LLMs (RAG Territorial):** Integrar modelo de linguagem natural permitindo que o gestor faça perguntas abertas em linguagem natural (*"Qual subprefeitura da Zona Sul apresenta maior urgência para implantação de uma nova unidade Teia?"*).
4. **Módulo de Cadastro de Demandas Comunitárias:** Permitir que associações de bairro e coletivos periféricos registrem formalmente pedidos de caravanas ou novos pontos de capacitação.

---

## 16. Instruções Completas para Execução (Banca Avaliadora)

### Opção A — Acesso Direto pela Web (Recomendado)
A aplicação está disponível e publicada na web em:  
🔗 **[https://adesampa-territorios.streamlit.app](https://adesampa-territorios.streamlit.app)** *(link configurável após publicação)*

---

### Opção B — Execução Local (Rápida e Sem Docker)

#### Requisitos do Ambiente
- Python 3.10 ou superior instalado.
- Gerenciador de pacotes `pip`.
- Navegador web moderno (Chrome, Edge, Firefox ou Safari).

#### ⚡ Execução Expressa em 1 Clique (Scripts Automatizados)
Para máxima facilidade da banca avaliadora, o repositório já inclui scripts prontos que realizam a criação do ambiente virtual, instalação de bibliotecas e inicialização com um único clique:
- **No Windows:** Dê um duplo-clique no arquivo `run.bat` (ou execute `.\run.bat` no terminal).
- **No Linux / macOS:** Execute no terminal:
  ```bash
  chmod +x run.sh && ./run.sh
  ```

---

#### 🛠️ Passo a Passo Manual de Instalação e Execução

1. **Clonar o Repositório ou descompactar a pasta:**
   ```bash
   git clone https://github.com/[seu-usuario]/adesampa-territorios-inteligentes.git
   cd adesampa-territorios-inteligentes
   ```

2. **Criar e ativar um ambiente virtual (recomendado):**
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a aplicação:**
   ```bash
   streamlit run app.py
   ```
   A aplicação abrirá automaticamente no seu navegador padrão no endereço: `http://localhost:8501`.

---

### Execução de Testes Automatizados
Para rodar a suíte de testes unitários:
```bash
pytest
```

