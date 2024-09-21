# Usar uma imagem base do Python
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de requirements para o container
COPY requirements.txt .
COPY . .

# Atualizar pip e instalar as dependências do Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto para o container
COPY . .

# Definir a variável de ambiente para garantir que o output do Python não seja armazenado em buffer
ENV PYTHONUNBUFFERED 1

# Expor a porta 8000
EXPOSE 8000

# Comando para rodar o servidor do Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
