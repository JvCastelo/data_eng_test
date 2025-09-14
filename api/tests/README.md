# Testes da API

Este diretório contém uma suíte completa de testes para a API usando pytest.

## Como executar os testes

```bash
# Executar todos os testes
uv run python -m pytest tests/ -v

# Executar testes específicos
uv run python -m pytest tests/test_auth_automated.py::TestAuthentication -v

# Executar com cobertura (se disponível)
uv run python -m pytest tests/ --cov=. --cov-report=html

# Executar apenas testes de autenticação
uv run python -m pytest tests/test_auth_automated.py -v

# Executar apenas testes de modelos
uv run python -m pytest tests/test_models.py -v
```

## Estrutura dos testes

### `test_auth_automated.py`
Testes automatizados para o sistema de autenticação:

- **TestAuthentication**: Testa autenticação por API Key
  - Verificação de API keys válidas/inválidas
  - Endpoints protegidos
  - Tratamento de erros de autenticação
- **TestDataEndpoints**: Testa endpoints de dados
  - Campos disponíveis
  - Paginação
  - Validação de parâmetros
- **TestRootEndpoint**: Testa endpoints públicos
  - Documentação Swagger
  - Endpoint raiz

### `test_models.py`
Testes para os modelos de dados:

- **TestUserModel**: Testa modelo User
  - Criação de usuários
  - Constraints de unicidade
  - Relacionamentos
- **TestApiKeyModel**: Testa modelo ApiKey
  - Criação de API keys
  - Valores padrão
  - Relacionamentos com usuários
- **TestDataModel**: Testa modelo Data
  - Criação de registros
  - Campos opcionais
- **TestHashFunction**: Testa funções de hash
  - Consistência do hash
  - Diferenças entre keys

### `conftest.py`
Configuração global para os testes:
- Fixtures compartilhadas
- Configuração do banco de teste
- Sessões de teste

### `test_auth.py`
Script manual de teste (legado):
- Testes manuais para verificação rápida
- Requer servidor rodando

## Funcionalidades testadas

### Autenticação
1. **API Keys válidas**: Verificação de keys corretas
2. **API Keys inválidas**: Rejeição de keys incorretas
3. **Keys inativas**: Bloqueio de keys desabilitadas
4. **Headers malformados**: Tratamento de erros de formato
5. **Usuários inexistentes**: Tratamento de relacionamentos quebrados

### Endpoints
1. **Endpoints protegidos**: Verificação de autenticação obrigatória
2. **Endpoints públicos**: Acesso sem autenticação
3. **Paginação**: Validação de parâmetros de página
4. **Campos**: Listagem de campos disponíveis
5. **Dados**: Busca com filtros e paginação

### Modelos
1. **Constraints**: Validação de unicidade e integridade
2. **Relacionamentos**: Verificação de foreign keys
3. **Valores padrão**: Teste de campos opcionais
4. **Hash**: Consistência e segurança

## Configuração

Os testes usam bancos SQLite separados para isolamento:
- Cada teste tem seu próprio banco limpo
- Fixtures garantem dados consistentes
- Rollback automático após cada teste

## Dependências

- pytest
- fastapi
- sqlalchemy
- httpx (para TestClient)

## Exemplo de execução

```bash
# Executar todos os testes com output detalhado
uv run python -m pytest tests/ -v --tb=short

# Executar apenas testes de autenticação
uv run python -m pytest tests/test_auth_automated.py::TestAuthentication::test_verify_valid_api_key -v

# Executar com relatório de cobertura
uv run python -m pytest tests/ --cov=. --cov-report=term-missing
```
