# Docker Setup - Teste Data Eng

Este documento explica como executar os componentes API e ETL usando Docker Compose.

## Estrutura dos Serviços

O docker-compose inclui os seguintes serviços:

- **postgres**: Banco de dados PostgreSQL
- **api**: Serviço FastAPI
- **etl**: Serviço ETL para processamento de dados

## Pré-requisitos

- Docker
- Docker Compose

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
# Configurações do Banco de Dados
DB_HOST_TARGET=postgres
DB_PORT_TARGET=5432
DB_NAME_TARGET=teste_data_eng
DB_USER_TARGET=postgres
DB_PASSWORD_TARGET=postgres123

# Configurações da API Externa (para o ETL)
API_BASE_URL=http://api:8000
API_KEY=your_api_key_here

# Configurações de Log
LOG_LEVEL=INFO
```

### 2. Executar os Serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ou usar o script de conveniência
./docker-commands.sh up
```

## Comandos Úteis

### Script de Conveniência

Use o script `docker-commands.sh` para comandos comuns:

```bash
# Iniciar serviços
./docker-commands.sh up

# Parar serviços
./docker-commands.sh down

# Ver logs
./docker-commands.sh logs

# Ver logs específicos
./docker-commands.sh api-logs
./docker-commands.sh etl-logs
./docker-commands.sh db-logs

# Acessar shell dos containers
./docker-commands.sh shell-api
./docker-commands.sh shell-etl
./docker-commands.sh shell-db

# Executar ETL
./docker-commands.sh run-etl --start-ts 2024-01-01 --end-ts 2024-01-02

# Status dos serviços
./docker-commands.sh status
```

### Comandos Docker Compose Diretos

```bash
# Construir imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar serviços
docker-compose restart

# Status dos serviços
docker-compose ps
```

## Executando o ETL

### Via Script de Conveniência

```bash
./docker-commands.sh run-etl --start-ts 2024-01-01 --end-ts 2024-01-02 --fields wind_speed,power
```

### Via Docker Compose Direto

```bash
docker-compose exec etl python main.py --start-ts 2024-01-01 --end-ts 2024-01-02
```

### Via Shell do Container

```bash
# Entrar no container
./docker-commands.sh shell-etl

# Dentro do container, executar:
python main.py --start-ts 2024-01-01 --end-ts 2024-01-02 --fields wind_speed,power,ambient_temperature
```

## Acessando os Serviços

- **API**: http://localhost:8000
- **Banco de Dados**: localhost:5432
- **Documentação da API**: http://localhost:8000/docs

## Desenvolvimento

### Modo de Desenvolvimento

Os containers estão configurados para desenvolvimento com:

- Volume mounting para código fonte
- Hot reload na API
- Logs em tempo real

### Debugging

```bash
# Ver logs em tempo real
docker-compose logs -f

# Entrar no container para debug
docker-compose exec api bash
docker-compose exec etl bash

# Verificar status dos serviços
docker-compose ps
```

## Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover volumes (CUIDADO: apaga dados do banco)
docker-compose down -v

# Remover imagens
docker-compose down --rmi all
```

## Troubleshooting

### Problemas Comuns

1. **Porta já em uso**: Verifique se a porta 8000 ou 5432 não estão sendo usadas
2. **Erro de conexão com banco**: Aguarde o healthcheck do PostgreSQL completar
3. **Erro de permissão**: Execute `chmod +x docker-commands.sh`

### Logs de Debug

```bash
# Ver logs detalhados
docker-compose logs -f --tail=100

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f etl
docker-compose logs -f postgres
```

### Verificar Conectividade

```bash
# Testar conexão com a API
curl http://localhost:8000/

# Testar conexão com banco
docker-compose exec postgres pg_isready -U postgres
```

