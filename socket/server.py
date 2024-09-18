import socket
import threading
import subprocess
import requests
import json
from datetime import datetime
import sys

sys.stdout.reconfigure(line_buffering=True)
SERVER_IP = "0.0.0.0"
SERVER_PORT = 8080
BUFFER_SIZE = 1024

# Função para enviar dados para o Elasticsearch
def enviar_dados_para_elasticsearch(num_clientes):
    url = f'http://localhost:9200/num_clientes/_doc/'
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

def enviar_para_tcp(engine_name, port, powmin, powmax):
    try:
        # Conectar ao servidor TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((engine_name, port))
            # Enviar os dados como JSON
            request_data = json.dumps({"powmin": powmin, "powmax": powmax})
            tcp_socket.sendall(request_data.encode('utf-8'))
            # Receber a resposta
            response = tcp_socket.recv(BUFFER_SIZE).decode('utf-8')
            print(f"Resposta do servidor TCP: {response}")
    except socket.error as e:
        print(f"Erro ao enviar dados para a engine {engine_name}: {e}")

def handle_client(client_socket, address, client_sockets):
    print(f"Novo cliente conectado, IP: {address[0]}, Porta: {address[1]}")
    
    # Enviar número de clientes conectados ao Elasticsearch
    num_clientes = len([sock for sock in client_sockets if sock is not None])
    # enviar_dados_para_elasticsearch(num_clientes)
    
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
                enviar_para_tcp('mpi-engine-deployment', 8081, powmin, powmax)
                # enviar_para_docker('c_engine', powmin, powmax)
                enviar_para_tcp('spark-engine-deployment', 7071, powmin, powmax)
            
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
    # enviar_dados_para_elasticsearch(num_clientes)

def main():
    print("Teste")
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
