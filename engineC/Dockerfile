# Usar uma imagem base com GCC e Make pré-instalados
FROM gcc:latest

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o código fonte para o diretório de trabalho
COPY . /app

# Compilar o código C
RUN gcc -o jogo_da_vida jogoVida.c

# Comando para rodar o executável
CMD ["./jogo_da_vida"]