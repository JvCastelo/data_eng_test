# Testes da API

Este diretório contém os testes essenciais da API usando pytest.

## Como executar os testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar testes específicos
python -m pytest tests/test_essential.py::TestRootEndpoint -v

# Executar com cobertura (se disponível)
python -m pytest tests/ --cov=. --cov-report=html
```

## Estrutura dos testes

### `test_essential.py`
Contém testes essenciais para as principais funcionalidades da API:

- **TestRootEndpoint**: Testa o endpoint raiz (`/`)
- **TestFieldsEndpoint**: Testa o endpoint de campos disponíveis (`/api/v1/data/fields`)
- **TestDataEndpoint**: Testa o endpoint principal de dados (`/api/v1/data/`)

### Funcionalidades testadas

1. **Endpoint raiz**: Verifica se a API está funcionando
2. **Campos disponíveis**: Lista os campos que podem ser consultados
3. **Busca de dados**: 
   - Banco vazio
   - Com dados de exemplo
   - Paginação
   - Filtros de data
   - Seleção de campos específicos
4. **Tratamento de erros**:
   - Campos inválidos
   - Parâmetros de paginação inválidos
   - Formato de data inválido

## Configuração

Os testes usam um banco SQLite em memória para isolamento e velocidade. Cada teste tem seu próprio banco limpo através dos fixtures `setup_database` e `sample_data`.

## Dependências

- pytest
- fastapi
- sqlalchemy
- httpx (para TestClient)
