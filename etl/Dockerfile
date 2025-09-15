FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instalar uv (gerenciador de pacotes Python)
RUN pip install uv

# Instalar dependências Python
RUN uv sync --frozen

# Copiar código da aplicação
COPY . .

# Comando padrão (mantém container rodando)
CMD ["tail", "-f", "/dev/null"]

