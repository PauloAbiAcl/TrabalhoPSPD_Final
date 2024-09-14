from pyspark.sql import SparkSession
import uuid
import re
import time
from datetime import datetime

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

def DumpTabul(tabul, tam, first, last, msg):
    for i in range(first, last + 1):
        print("=", end="")
    print()
    for i in range(first, last + 1):
        for j in range(first, last + 1):
            print('X' if tabul[i][j] == 1 else '.', end='')
        print('|')
    for i in range(first, last + 1):
        print("=", end="")
    print()

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
    json = {"status": 1 if Correto(tabulIn, tam) else 0, "mode": "Spark", "time": delta_tempo.total_seconds(), "potency": potencia}
    print("ENVIANDO=", json)

if __name__ == "__main__":
    spark = SparkSession.builder.master("local[6]").appName("GameOfLife").getOrCreate()
    potencia_min = 3
    potencia_max = 8
    for potencia in range(potencia_min, potencia_max + 1):
        a = list(range(potencia_min, potencia_max + 1))
        a_rdd = spark.sparkContext.parallelize(a)
        a_rdd.foreach(lambda x: jogoVida(x))
    spark.stop()
