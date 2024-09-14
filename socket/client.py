import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
BUFFER_SIZE = 1024

def main():
    # Cria o socket do cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Conecta ao servidor
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Conectado ao servidor em {SERVER_IP}:{SERVER_PORT}")

        while True:
            message = input("Digite a mensagem no formato <num1,num2>: ")

            # Envia a mensagem para o servidor
            client_socket.sendall(message.encode('utf-8'))
            
    except KeyboardInterrupt:
        print("\nEncerrando o cliente.")
    
    finally:
        # Fecha o socket do cliente
        client_socket.close()

if __name__ == "__main__":
    main()
