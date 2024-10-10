# Usa a imagem oficial do Python como base
FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos e instala as dependências
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia o restante dos arquivos da aplicação
COPY . .

# Comando para iniciar a aplicação
CMD ["python", "Main.py"]  # Substitua "Main.py" pelo teu arquivo principal
