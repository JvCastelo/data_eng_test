-- Script de inicialização do banco de dados
-- Este script será executado automaticamente quando o container PostgreSQL for criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar schema se necessário
-- CREATE SCHEMA IF NOT EXISTS public;

-- As tabelas serão criadas automaticamente pelos modelos SQLAlchemy
-- quando os serviços API e ETL forem executados

