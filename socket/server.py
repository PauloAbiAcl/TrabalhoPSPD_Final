import socket
import threading
import subprocess
import requests
import json
from datetime import datetime
import sys
from kubernetes import client, config

sys.stdout.reconfigure(line_buffering=True)

# Carregar configuração dentro do pod Kubernetes
config.load_incluster_config()

SERVER_IP = "0.0.0.0"
SERVER_PORT = 8080
BUFFER_SIZE = 1024

# Função para enviar dados para o Elasticsearch
def enviar_dados_para_elasticsearch(num_clientes):
    url = f'http://elasticsearch-service:9200/num_clientes/_doc/'
    headers = {'Content-Type': 'application/json'}
    data = {
        "num_clientes": num_clientes,
        "timestamp": datetime.now().isoformat() 
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Dados de clientes conectados enviados com sucesso para o Elasticsearch.")
    else:
        print(f"Erro ao enviar dados: {response.status_code} - {response.text}")


def executar_comando_no_pod(pod_name, command):
    try:
        kubectl_command = [
            "kubectl", "exec", pod_name, "--", "sh", "-c", command
        ]
        subprocess.run(kubectl_command, check=True)
        print(f"Comando executado com sucesso no pod {pod_name}: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando no pod {pod_name}: {e}")

def get_pod_name(label_selector, namespace="default"):
    try:
        kubectl_command = [
            "kubectl", "get", "pods", "-l", f"{label_selector}", "-o", "jsonpath={.items[0].metadata.name}"
        ]
        pod_name = subprocess.check_output(kubectl_command).decode('utf-8').strip()
        print(f"Nome do pod com label {label_selector}: {pod_name}")
        return pod_name
    except client.rest.ApiException as e:
        print(f"Erro ao obter o nome do pod com label {label_selector}: {e}")
        return None

def enviar_para_docker(engine_name, powmin, powmax):
    if engine_name == 'mpi-engine':
        comando = f"mpirun --allow-run-as-root -np 2 ./jogoVidaMPI {powmin} {powmax}"
    elif engine_name == 'c-engine':
        comando = f"./jogoVida {powmin} {powmax}"
    elif engine_name == 'spark-engine':
        comando = f"python jogoVidaSpark.py {powmin} {powmax}"
    else:
        print(f"Engine desconhecida: {engine_name}")
        return

    # Buscar o nome do pod dinamicamente com base no label
    pod_name = get_pod_name(f"app={engine_name}", "default")
    if pod_name:
        executar_comando_no_pod(pod_name, comando)
    else:
        print(f"Erro: não foi possível encontrar o pod para {engine_name}")

def handle_client(client_socket, address, client_sockets):
    print(f"Novo cliente conectado, IP: {address[0]}, Porta: {address[1]}")
    sys.stdout.flush()
    
    # Enviar número de clientes conectados ao Elasticsearch
    num_clientes = len([sock for sock in client_sockets if sock is not None])
    enviar_dados_para_elasticsearch(num_clientes)
    
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                print(f"Host desconectado, IP: {address[0]}, Porta: {address[1]}")
                break
            
            message = data.decode()
            
            if message.startswith('<') and message.endswith('>'):
                message = message[1:-1]  # Remove < e >
                powmin, powmax = map(int, message.split(','))
                
                print(f"Cliente {address[0]}:{address[1]} enviou: POWMIN={powmin}, POWMAX={powmax}")
                
                # Envia para as diferentes engines
                enviar_para_docker('mpi-engine', powmin, powmax)
                # enviar_para_docker('c_engine', powmin, powmax)
                enviar_para_docker('spark-engine', powmin, powmax)
            
            else:
                print("Formato da mensagem inválido.")
        
        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente, IP: {address[0]}, Porta: {address[1]}")
            break
        
        except Exception as e:
            print(f"Erro: {e}")
            break

    # Remove o cliente desconectado da lista e atualizar o número de clientes
    for i in range(len(client_sockets)):
        if client_sockets[i] == client_socket:
            client_sockets[i] = None
            break
    client_socket.close()

    # Enviar o número atualizado de clientes conectados
    num_clientes = len([sock for sock in client_sockets if sock is not None])
    enviar_dados_para_elasticsearch(num_clientes)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    print("Servidor escutando na porta 8080...")

    max_clients = 10
    client_sockets = [None] * max_clients

    while True:
        try:
            client_socket, address = server_socket.accept()

            for i in range(max_clients):
                if client_sockets[i] is None:
                    client_sockets[i] = client_socket
                    break

            client_thread = threading.Thread(target=handle_client, args=(client_socket, address, client_sockets))
            client_thread.start()
        
        except KeyboardInterrupt:
            print("Encerrando servidor...")
            break
        
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

    # Fechar o socket do servidor
    server_socket.close()

if __name__ == "__main__":
    main()
