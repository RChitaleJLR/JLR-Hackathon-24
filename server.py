import socket
import threading
import json

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
all_data = []
clients = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode(FORMAT))
        except Exception as e:
            print(f"Failed to send message to client: {e}")

def request_location(conn):
    try:
        conn.send("Please send pothole location.".encode(FORMAT))
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            location_data = conn.recv(msg_length).decode(FORMAT)
            return json.loads(location_data)
    except Exception as e:
        print(f"Failed to get location from client: {e}")
    return None

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    data = json.loads(msg)
                    print(f"[{addr}] {data}")
                    all_data.append(data)
                    # Write to JSON file
                    with open('received_vehicle_data.json', 'w') as json_file:
                        json.dump(all_data, json_file)
                    print("Data saved to received_vehicle_data.json")
                    # Handle request field
                    requests = data.get("Request", [])
                    for req in requests:
                        if req.lower() == "parking":
                            conn.send("Park at McDonalds".encode(FORMAT))
                    # Handle warning field
                    warnings = data.get("Warning", [])
                    for warn in warnings:
                        if warn.lower() == "pothole":
                            location = request_location(conn)
                            if location:
                                broadcast(f"Pothole detected at {location['GPS']['latitude']}, {location['GPS']['longitude']}!")
        except ValueError as e:
            print(f"Invalid message length received: {msg_length} - {e}")
    conn.close()
    clients.remove(conn)

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        
print("[STARTING] Server is starting...")
start()