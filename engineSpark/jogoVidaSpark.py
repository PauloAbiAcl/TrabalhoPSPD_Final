import socket
import threading
import json
from pyspark.sql import SparkSession
import re
from datetime import datetime
import requests
import sys

sys.stdout.reconfigure(line_buffering=True)
# Função para enviar dados para o Elasticsearch
def enviar_dados_para_elasticsearch(data):
    url = f'http://elasticsearch:9200/tempo_spark_engine/_doc/'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Dados enviados com sucesso para o Elasticsearch.")
    else:
        print(f"Erro ao enviar dados: {response.status_code} - {response.text}")

def extrairNumeros(texto):
    padrao = r'<(\d+),(\d+)>'
    correspondencias = re.search(padrao, texto)
    if correspondencias:
        numero1 = int(correspondencias.group(1))
        numero2 = int(correspondencias.group(2))
        if numero1 > numero2:
            numero1, numero2 = numero2, numero1
        return numero1, numero2
    return None, None

def matrix(m, n):
    return [[0 for _ in range(n)] for _ in range(m)]

def Correto(tabul, tam):
    cnt = 0
    for i in range(tam + 2):
        for j in range(tam + 2):
            cnt += tabul[i][j]
    return cnt == 5 and tabul[tam - 2][tam - 1] and \
           tabul[tam - 1][tam] and \
           tabul[tam][tam - 2] and \
           tabul[tam][tam - 1] and \
           tabul[tam][tam]

def InitTabul(tam):
    tabulIn = matrix(tam + 2, tam + 2)
    tabulOut = matrix(tam + 2, tam + 2)
    tabulIn[1][2] = 1
    tabulIn[2][3] = 1
    tabulIn[3][1] = 1
    tabulIn[3][2] = 1
    tabulIn[3][3] = 1
    return tabulIn, tabulOut

def UmaVida(tabulIn, tabulOut, tam):
    for i in range(1, tam + 1):
        for j in range(1, tam + 1):
            vizviv = tabulIn[i - 1][j - 1] + tabulIn[i - 1][j] + tabulIn[i - 1][j + 1] + \
                     tabulIn[i][j - 1] + tabulIn[i][j + 1] + \
                     tabulIn[i + 1][j - 1] + tabulIn[i + 1][j] + tabulIn[i + 1][j + 1]
            if tabulIn[i][j] and vizviv < 2:
                tabulOut[i][j] = 0
            elif tabulIn[i][j] and vizviv > 3:
                tabulOut[i][j] = 0
            elif not tabulIn[i][j] and vizviv == 3:
                tabulOut[i][j] = 1
            else:
                tabulOut[i][j] = tabulIn[i][j]

def jogoVida(potencia):
    tam = 1 << potencia
    tabulIn, tabulOut = InitTabul(tam)
    t1 = datetime.now()
    for _ in range(2 * (tam - 3)):
        UmaVida(tabulIn, tabulOut, tam)
        UmaVida(tabulOut, tabulIn, tam)
    t2 = datetime.now()
    delta_tempo = t2 - t1
    if Correto(tabulIn, tam):
        print(f"*Ok, RESULTADO CORRETO* - Potência: {potencia}")
    else:
        print(f"**Not Ok, RESULTADO ERRADO** - Potência: {potencia}")
    json_data = {
        "time": delta_tempo.total_seconds(),
        "tamanho": tam,
        "engine_name": "spark_engine",
        "timestamp": datetime.now().isoformat() 
    }
    enviar_dados_para_elasticsearch(json_data)

def handle_client_conncetion(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Recebido: {request}")
        
        try:
            data = json.loads(request)
            num1 = int(data.get('powmin'))
            num2 = int(data.get('powmax'))

            if not isinstance(num1, int) or not isinstance(num2, int):
                client_socket.send("Os valores devem ser inteiros".encode('utf-8'))
                return

            spark = SparkSession.builder.master("local[6]").appName("GameOfLife").getOrCreate()
            potencias = list(range(num1, num2 + 1))
            potenciasrdd = spark.sparkContext.parallelize(potencias, len(potencias))
            potenciasrdd.map(lambda x: jogoVida(x)).collect()
            spark.stop()

            client_socket.send("Processamento concluído com sucesso".encode('utf-8'))
        except json.JSONDecodeError:
            client_socket.send("Erro ao decodificar JSON".encode('utf-8'))
    finally:
        client_socket.close()

def start_server(host='0.0.0.0', port=7071):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Servidor ouvindo na porta {port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão recebida de {addr}")
        client_handler = threading.Thread(target=handle_client_conncetion, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
