# Use uma imagem base Python
FROM python:3.9

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários
COPY server.py /app/
COPY requirements.txt /app/

# Instale as dependências
RUN pip install -r requirements.txt

# Exponha a porta usada pelo servidor
EXPOSE 8080

# Comando para rodar o servidor
CMD ["python", "server.py"]
