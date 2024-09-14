from pyspark.sql import SparkSession
import requests
import uuid
import re
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
    for i in range(tam+2):
        for j in range(tam+2):
            cnt += tabul[i][j]
    return cnt == 5 and tabul[tam-2][tam-1] and tabul[tam-1][tam] and tabul[tam][tam-2] and tabul[tam][tam-1] and tabul[tam][tam]

def InitTabul(tam):
    tabulIn = matrix(tam+2, tam+2)
    tabulOut = matrix(tam+2, tam+2)
    tabulIn[1][2] = 1
    tabulIn[2][3] = 1
    tabulIn[3][1] = 1
    tabulIn[3][2] = 1
    tabulIn[3][3] = 1
    return tabulIn, tabulOut

def UmaVida(tabulIn, tabulOut, tam):
    for i in range(1, tam+1):
        for j in range(1, tam+1):
            vizviv = tabulIn[i-1][j-1] + tabulIn[i-1][j] + tabulIn[i-1][j+1] + tabulIn[i][j-1] + tabulIn[i][j+1] + tabulIn[i+1][j-1] + tabulIn[i+1][j] + tabulIn[i+1][j+1]
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
    
    t_init = datetime.now()
    UmaVida(tabulIn, tabulOut, tam)
    t_comp = datetime.now()
    UmaVida(tabulOut, tabulIn, tam)
    t_fim = datetime.now()
    
    delta_init = t_comp - t_init
    delta_comp = t_fim - t_comp
    delta_fim = t_fim - t_comp  # Corrigido: delta_fim deve ser a diferença após o segundo UmaVida
    delta_total = delta_init + delta_comp + delta_fim

    resultado = "CORRETO" if Correto(tabulIn, tam) else "ERRADO"
    
    print(f"mpi_engine  | **RESULTADO {resultado}**")
    print(f"mpi_engine  | tam={tam}; tempos: init={delta_init.total_seconds():.7f}, comp={delta_comp.total_seconds():.7f}, fim={delta_fim.total_seconds():.7f}, tot={delta_total.total_seconds():.7f}")
    print("mpi_engine  |", 1 if resultado == "CORRETO" else 0)

    guid = str(uuid.uuid4())
    json = {"status": 1 if resultado == "CORRETO" else 0, "mode": "Spark", "time": delta_total.total_seconds(), "potency": potencia}

def main():
    potencias = list(range(3, 11))  # Potências de 3 a 10
    spark = SparkSession.builder.master("local[6]").appName("MyProgram").getOrCreate()
    rdd = spark.sparkContext.parallelize(potencias)
    rdd.foreach(lambda x: jogoVida(x))
    spark.stop()

if __name__ == "__main__":
    main()
