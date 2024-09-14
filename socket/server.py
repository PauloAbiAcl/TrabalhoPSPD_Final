import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
BUFFER_SIZE = 1024

def handle_client(client_socket, address):
    print(f"Novo cliente conectado, IP: {address[0]}, Porta: {address[1]}")
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                print(f"Host desconectado, IP: {address[0]}, Porta: {address[1]}")
                break
            
            message = data.decode()
            
            if message.startswith('<') and message.endswith('>'):
                message = message[1:-1]  # Remove < e >
                num1, num2 = map(int, message.split(','))
                
                print(f"Cliente {address[0]}:{address[1]} enviou: num1={num1}, num2={num2}")
                
                sum_result = num1 + num2

                response = f"Soma: {sum_result}"
                client_socket.send(response.encode())
            
            else:
                print("Formato da mensagem inválido.")
        
        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente, IP: {address[0]}, Porta: {address[1]}")
            break
        
        except Exception as e:
            print(f"Erro: {e}")
            break

    client_socket.close()

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

            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
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
