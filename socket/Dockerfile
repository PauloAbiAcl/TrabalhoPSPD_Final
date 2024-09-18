# Use uma imagem base Python
FROM python:3.9

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários
COPY server.py /app/
COPY requirements.txt /app/

# Atualize os pacotes e instale curl
RUN apt-get update && apt-get install -y curl

# Instale kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Instale as dependências Python
RUN pip install -r requirements.txt
RUN pip install kubernetes

# Exponha a porta usada pelo servidor
EXPOSE 8080

# Comando para rodar o servidor
CMD ["python", "server.py"]
