import socket
import os


received_folder_path = "C:/Users/HP/Desktop/apple/recieved_data"


def ensure_received_folder():
    if not os.path.exists(received_folder_path):
        os.makedirs(received_folder_path)


def log_to_file(message):
    with open("output.txt", "a") as f:
        f.write(message + "\n")


def handle_client(conn, addr):
    try:
        while True:
            
            command = conn.recv(1024).decode('utf-8', errors='ignore')
            if not command:
                break

            if command == 'SEND_FILE':
               
                filename_len = int(conn.recv(4).decode('utf-8'))
                filename = conn.recv(filename_len).decode('utf-8')

                
                file_size = int(conn.recv(8).decode('utf-8'))

                
                ensure_received_folder()

                file_path = os.path.join(received_folder_path, filename)
                with open(file_path, "wb") as f:
                    received = 0
                    while received < file_size:
                        data = conn.recv(4096)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)

                if received == file_size:
                    log_to_file(f"File received from {addr}: {filename} ({file_size} bytes)")
                    print(f"File '{filename}' saved in '{received_folder_path}'.")
                else:
                    log_to_file(f"Incomplete file received from {addr}: {filename}")
            elif command == 'EXIT':
                log_to_file(f"Client {addr} disconnected.")
                break
            else:
                log_to_file(f"Unexpected command: {command}")
    except Exception as e:
        log_to_file(f"Error handling client {addr}: {e}")
    finally:
        conn.close()


def start_server(port):
    while True:
        host = socket.gethostbyname(socket.gethostname())  
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"Server listening on {host}:{port}")

        conn, addr = server.accept()
        handle_client(conn, addr)

        restart = input("\nDo you want to restart as server or client? (y/n): ").strip().lower()
        if restart == 'n':
            break
        elif restart == 'y':
            role = input("Enter 's' for server or 'c' for client: ").strip().lower()
            if role == 'c':
                server.close()
                start_client(port)
                return  
        else:
            print("Invalid input. Exiting...")
            break


def start_client(port):
    server_ip = socket.gethostbyname(socket.gethostname())  
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, port))
        print(f"Connected to server at {server_ip}:{port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    while True:
        print("\n1. Send file\n2. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            file_path = input("Enter file path: ").strip()
            if not os.path.exists(file_path):
                print("File does not exist.")
                continue
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            try:
                client.sendall("SEND_FILE".encode())
               
                client.sendall(f"{len(file_name):04}".encode('utf-8'))
                client.sendall(file_name.encode('utf-8'))
                
                client.sendall(f"{file_size:08}".encode('utf-8'))

               
                with open(file_path, "rb") as f:
                    while chunk := f.read(4096):
                        client.sendall(chunk)
                print(f"File '{file_name}' sent successfully.")
            except Exception as e:
                print(f"Error during file transfer: {e}")
        elif choice == '2':
            client.sendall("EXIT".encode())
            client.close()
            break
        else:
            print("Invalid choice.")

        restart = input("\nDo you want to send or receive files again? (y/n): ").strip().lower()
        if restart != 'y':
            print("\nExiting client...")
            break


def run_server_client():
    while True:
        role = input("Enter 's' for server or 'c' for client: ").strip().lower()
        if role == 's':
            port = int(input("Enter port number (e.g., 5000): ").strip())
            start_server(port)
        elif role == 'c':
            port = int(input("Enter port number to connect to: ").strip())
            start_client(port)
        else:
            print("Invalid choice. Please enter 's' or 'c'.")

        restart = input("\nDo you want to restart as server or client? (y/n): ").strip().lower()
        if restart != 'y':
            print("\nExiting...")
            break

if __name__ == "__main__":
    run_server_client()
