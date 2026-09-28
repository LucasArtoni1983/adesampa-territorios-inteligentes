# Ade Sampa — api-contracts.md

## Contratos de API

Todos os endpoints da aplicação devem seguir padrões consistentes de RESTful API.

### Padrão de Resposta de Sucesso
```json
{
  "success": true,
  "data": {},
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

### Padrão de Resposta de Erro
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Parâmetro inválido ou ausente.",
    "details": []
  }
}
```

### Endpoints Principais (Exemplo)
- `GET /api/v1/indicadores`: Lista indicadores públicos municipais com filtros por tema, região e ano.
- `GET /api/v1/equipamentos`: Lista equipamentos ou serviços georreferenciados por distrito ou proximidade.
- `POST /api/v1/analise-ia`: Processa uma consulta analítica orientada a dados para apoio à decisão.
