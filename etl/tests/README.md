# Testes Essenciais do Projeto ETL

Este diretório contém os testes essenciais para garantir que o projeto ETL funcione corretamente.

## Estrutura Simplificada

```
tests/
├── conftest.py          # Configuração global e fixtures
├── test_models.py       # Testes essenciais para modelos (3 testes)
├── test_etl.py          # Testes essenciais para ETL (3 testes)
├── test_database.py     # Testes essenciais para banco (3 testes)
├── test_scripts.py       # Testes essenciais para scripts (2 testes)
└── README.md            # Este arquivo

pyproject.toml           # Configuração do pytest
```

**Total: 11 testes essenciais** ✅

## Tipos de Testes

### 🧪 Testes Unitários (`@pytest.mark.unit`)
- Testam componentes isolados
- Execução rápida

### 🗄️ Testes de Banco (`@pytest.mark.database`)
- Testam operações de banco de dados
- Verificam constraints importantes

## Como Executar

### Instalar Dependências
```bash
uv sync --extra test
```

### Executar Todos os Testes
```bash
uv run pytest
```

### Executar por Categoria
```bash
uv run pytest -m unit      # Testes unitários
uv run pytest -m database # Testes de banco
```

### Executar com Cobertura
```bash
uv run pytest --cov=.
```

## Testes Incluídos

### **Modelos** (`test_models.py`)
- ✅ Criação de sinais
- ✅ Criação de dados
- ✅ Constraint de timestamp

### **ETL** (`test_etl.py`)
- ✅ Inicialização da classe
- ✅ Transformação de dados
- ✅ Carregamento no banco

### **Banco** (`test_database.py`)
- ✅ Criação de tabelas
- ✅ Operações CRUD básicas
- ✅ Constraints de dados

### **Scripts** (`test_scripts.py`)
- ✅ Geração de nomes de sinais
- ✅ População de sinais

## Fixtures Essenciais

- `test_session` - Sessão de banco isolada
- `sample_signals` - Sinais de exemplo
- `sample_raw_data` - Dados brutos da API
- `sample_transformed_data` - DataFrame pandas

## Cobertura Atual

**74% de cobertura** com apenas 11 testes essenciais! 🎯

Os testes cobrem:
- ✅ Funcionalidades críticas
- ✅ Constraints importantes
- ✅ Fluxo principal do ETL
- ✅ Operações de banco básicas
