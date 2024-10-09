# Usa a imagem oficial do Python como base
FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos e instala as dependências
COPY Requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos da aplicação
COPY . .

# Comando para iniciar a aplicação
CMD ["python", "app.py"]  # Substitua "app.py" pelo seu arquivo principal
