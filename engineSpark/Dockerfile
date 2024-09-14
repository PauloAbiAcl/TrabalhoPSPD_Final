ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

COPY --from=py3 / /
EXPOSE 7071

WORKDIR /app
COPY jogoVidaSpark.py /app/jogoVidaSpark.py

# Instalação das dependências Python
RUN pip install pyspark==3.4.1
RUN pip install requests
RUN pip install asyncio
RUN pip install numpy

CMD ["python3", "-u", "jogoVidaSpark.py"]
