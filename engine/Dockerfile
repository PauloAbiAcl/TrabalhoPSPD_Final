FROM ubuntu:latest

# Instalar dependências e o OpenMPI
RUN apt-get update && \
    apt-get install -y build-essential openmpi-bin openmpi-common libopenmpi-dev curl && \
    apt-get clean

# Copiar o código MPI para o container
COPY jogoVidaMPI.c /usr/src/app/

# Definir o diretório de trabalho
WORKDIR /usr/src/app/

# Compilar o código MPI
RUN mpicc -o jogoVidaMPI jogoVidaMPI.c

# Definir variáveis de ambiente para permitir execução como root
ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# Expor uma porta para comunicação (se necessário)
EXPOSE 8081

# Manter o container em execução indefinidamente
CMD ["mpirun", "-np", "2" "./jogoVidaMPI"]
