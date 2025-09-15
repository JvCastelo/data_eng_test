#!/bin/bash

# Script de conveniência para comandos Docker Compose

case "$1" in
    "up")
        echo "Iniciando todos os serviços..."
        docker-compose up -d
        ;;
    "down")
        echo "Parando todos os serviços..."
        docker-compose down
        ;;
    "build")
        echo "Construindo imagens..."
        docker-compose build
        ;;
    "logs")
        echo "Mostrando logs dos serviços..."
        docker-compose logs -f
        ;;
    "api-logs")
        echo "Mostrando logs da API..."
        docker-compose logs -f api
        ;;
    "etl-logs")
        echo "Mostrando logs do ETL..."
        docker-compose logs -f etl
        ;;
    "db-logs")
        echo "Mostrando logs do banco de dados..."
        docker-compose logs -f postgres
        ;;
    "shell-api")
        echo "Abrindo shell no container da API..."
        docker-compose exec api bash
        ;;
    "shell-etl")
        echo "Abrindo shell no container do ETL..."
        docker-compose exec etl bash
        ;;
    "shell-db")
        echo "Abrindo shell no container do banco de dados..."
        docker-compose exec postgres psql -U postgres -d teste_data_eng
        ;;
    "run-etl")
        echo "Executando ETL..."
        shift
        docker-compose exec etl python main.py "$@"
        ;;
    "restart")
        echo "Reiniciando todos os serviços..."
        docker-compose restart
        ;;
    "status")
        echo "Status dos serviços:"
        docker-compose ps
        ;;
    *)
        echo "Uso: $0 {up|down|build|logs|api-logs|etl-logs|db-logs|shell-api|shell-etl|shell-db|run-etl|restart|status}"
        echo ""
        echo "Comandos disponíveis:"
        echo "  up          - Inicia todos os serviços"
        echo "  down        - Para todos os serviços"
        echo "  build       - Constrói as imagens"
        echo "  logs        - Mostra logs de todos os serviços"
        echo "  api-logs    - Mostra logs da API"
        echo "  etl-logs    - Mostra logs do ETL"
        echo "  db-logs     - Mostra logs do banco de dados"
        echo "  shell-api   - Abre shell no container da API"
        echo "  shell-etl   - Abre shell no container do ETL"
        echo "  shell-db    - Abre shell no banco de dados"
        echo "  run-etl     - Executa o ETL com argumentos"
        echo "  restart     - Reinicia todos os serviços"
        echo "  status      - Mostra status dos serviços"
        echo ""
        echo "Exemplos:"
        echo "  $0 up"
        echo "  $0 run-etl --start-ts 2024-01-01 --end-ts 2024-01-02"
        echo "  $0 shell-etl"
        exit 1
        ;;
esac

