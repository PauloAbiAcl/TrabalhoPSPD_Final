import socket

def send_to_server(server_ip, server_port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        client_socket.sendall(message.encode('utf-8'))
        # response = client_socket.recv(1024).decode('utf-8')
        # print(f"Resposta do servidor {server_ip}:{server_port} -> {response}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client_socket.close()

def main():
    # Substitua pelos valores reais do IP e NodePort do serviço
    server_ip = "127.0.0.1"  # IP do nó Kubernetes
    server_port = 8080  # NodePort atribuído ao serviço

    while True:
        message = input("Digite a mensagem no formato <num1,num2>: ")
        # Envia a mensagem para o server.py que está escutando na porta especificada
        send_to_server(server_ip, server_port, message)

if __name__ == "__main__":
    main()
