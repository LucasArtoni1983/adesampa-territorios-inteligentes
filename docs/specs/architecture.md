# Ade Sampa — architecture.md

## Visão arquitetural

Aplicação web modular, robusta e orientada a dados, desenhada para simplicidade de execução, alta performance e manutenibilidade.

## Containers principais

- `apps/web` (ou `frontend`): interface do usuário interativa (React / Vite ou Next.js / TypeScript) com dashboards e mapas
- `apps/api` (ou `backend`): camada de serviços e APIs REST (Python/FastAPI ou Node.js/TypeScript)
- `packages/shared`: tipagens, contratos de dados e utilitários
- Armazenamento de dados: SQLite / PostgreSQL ou dados processados em JSON/GeoJSON para portabilidade imediata
- Cache / In-memory: otimização de consultas e dados agregados

## Padrões arquiteturais

- Clean Architecture e separação clara de responsabilidades
- Separação estrita entre camada visual, casos de uso/serviços e acesso a dados
- DTOs / Schemas de validação em todas as fronteiras (Zod / Pydantic)
- Tratamento uniforme e amigável de erros
- Observabilidade básica com logs estruturados
- Aderência às diretrizes de Clean Code e princípios SOLID

## Decisões arquiteturais registradas

- ADR-001: Escolha da stack de desenvolvimento web e dados
- ADR-002: Estratégia de obtenção e cacheamento de dados abertos municipais
- ADR-003: Padrão de visualização espacial / mapas
- ADR-004: Modelo de documentação de IA e Vibe Coding conforme Edital 005/2026
