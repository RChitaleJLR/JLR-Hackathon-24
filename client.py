import socket
import json
import time

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "10.255.71.154"  # Replace with your server's IP if not running on the same machine
ADDR = (SERVER, PORT)

def create_json_file():
    data = {
        "vehicle_id": "V5555",
        "timestamp": time.time(),
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        "speed": 60,
        "fuel_level": 85
    }
    with open('vehicle_data.json', 'w') as json_file:
        json.dump(data, json_file)
    return data

def send_json_data(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDR)
        message = json.dumps(data)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        s.send(send_length)
        s.send(message.encode(FORMAT))
        print("Data sent to server")
        s.send(DISCONNECT_MESSAGE.encode(FORMAT))

if __name__ == "__main__":
    vehicle_data = create_json_file()
    send_json_data(vehicle_data)
