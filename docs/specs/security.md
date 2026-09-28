# Ade Sampa — security.md

## Diretrizes de Segurança

Este documento especifica os controles e requisitos de segurança do projeto:

### Requisitos

- **Menor Privilégio:** Agentes e processos executam com permissões estritamente necessárias.
- **Validação de Entrada:** Todas as consultas, parâmetros de filtro e uploads devem ser sanitizados e validados por schemas.
- **Proteção contra Injeção:** Proibida concatenação de parâmetros em queries SQL ou comandos de sistema operacional.
- **Segredos:** Credenciais e chaves de API nunca devem ser versionadas no repositório. Uso de `.env.example` apenas com valores de modelo.
- **Tratamento Seguro de Erros:** Não exibir stack traces internos para o usuário final.
- **Privacidade e LGPD:** Dados públicos reais preservados; nenhum dado sensível desnecessário trafegado.
