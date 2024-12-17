from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import socket

app = Flask(__name__)
received_folder_path = "C:/Users/HP/Desktop/apple/recieved_data"

# Ensure the folder exists
def ensure_received_folder():
    if not os.path.exists(received_folder_path):
        os.makedirs(received_folder_path)

ensure_received_folder()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send_file():
    if request.method == 'POST':
        server_ip = request.form['server_ip']
        port = int(request.form['port'])
        file = request.files['file']
        if file:
            file_path = os.path.join(received_folder_path, file.filename)
            file.save(file_path)
            
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((server_ip, port))
                print(f"Connected to server at {server_ip}:{port}")

                client.sendall("SEND_FILE".encode())
                file_name = file.filename
                file_size = os.path.getsize(file_path)

                client.sendall(f"{len(file_name):04}".encode('utf-8'))
                client.sendall(file_name.encode('utf-8'))
                client.sendall(f"{file_size:08}".encode('utf-8'))

                with open(file_path, "rb") as f:
                    while chunk := f.read(4096):
                        client.sendall(chunk)
                client.close()
                print("File sent successfully!")
            except Exception as e:
                print(f"Error: {e}")
        
        return redirect(url_for('home'))
    return render_template('send.html')

@app.route('/receive', methods=['GET', 'POST'])
def receive_file():
    if request.method == 'POST':
        port = int(request.form['port'])
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((socket.gethostbyname(socket.gethostname()), port))
            server.listen()
            print(f"Server listening on port {port}")
            
            conn, addr = server.accept()
            command = conn.recv(1024).decode('utf-8', errors='ignore')
            if command == 'SEND_FILE':
                filename_len = int(conn.recv(4).decode('utf-8'))
                filename = conn.recv(filename_len).decode('utf-8')
                file_size = int(conn.recv(8).decode('utf-8'))

                file_path = os.path.join(received_folder_path, filename)
                with open(file_path, "wb") as f:
                    received = 0
                    while received < file_size:
                        data = conn.recv(4096)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                conn.close()
                print(f"File '{filename}' received and saved.")
        except Exception as e:
            print(f"Error: {e}")
        
        return redirect(url_for('home'))
    return render_template('receive.html')

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(received_folder_path, filename)

if __name__ == '__main__':
    app.run(debug=True)
