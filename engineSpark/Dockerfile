# Escolhendo uma imagem base com Python e Java
ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

# Copiando arquivos do primeiro estágio
COPY --from=py3 / / 

# Instalação das dependências Python
WORKDIR /app
COPY jogoVidaSpark.py /app/jogoVidaSpark.py
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN chmod +x /app/jogoVidaSpark.py

EXPOSE 7071

# Manter o container em execução indefinidamente
CMD ["python", "jogoVidaSpark.py"]
