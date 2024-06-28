import socket
import json
import time
import threading
import cv2
from matplotlib import pyplot as plt
import torch

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "10.255.71.154"  # Replace with your server's IP if not running on the same machine
ADDR = (SERVER, PORT)
SENSORS = {
    "speed": 60,
    "latitude":  37.7749,
    "longitude": -122.4194
}

def create_json_file(hazards=None):
   global SENSORS
   data = {
       "vehicle_id": "V1234",
       "timestamp": time.time(),
       "car_type": 1,
       "speed": SENSORS["speed"],
       "GPS": {
           "latitude": SENSORS["latitude"],
           "longitude": SENSORS["longitude"]
       },
       "Request": ["Parking"],
   }

   if hazards is not None and len(hazards)>0:
    data["Warning"] = hazards

    print(data)

   with open('vehicle_data.json', 'w') as json_file:
       json.dump(data, json_file)
   return data

def send_json_data(data, s):
   message = json.dumps(data)
   msg_length = len(message)
   send_length = str(msg_length).encode(FORMAT)
   send_length += b' ' * (HEADER - len(send_length))
   s.send(send_length)
   s.send(message.encode(FORMAT))
   print("Data sent to server")

def listen_for_server_messages(s):
   while True:
       try:
           message = s.recv(HEADER).decode(FORMAT)
           if message:
               print(f"Message from server: {message}")
               if "Please send pothole location" in message:
                   # Send the pothole location back to the server
                   global SENSORS
                   location_data = {
                       "GPS": {
                           "latitude": SENSORS["latitude"],
                           "longitude": SENSORS["longitude"],
                       }
                   }
                   response_message = json.dumps(location_data)
                   msg_length = len(response_message)
                   send_length = str(msg_length).encode(FORMAT)
                   send_length += b' ' * (HEADER - len(send_length))
                   s.send(send_length)
                   s.send(response_message.encode(FORMAT))
       except Exception as e:
           print(f"Error receiving message: {e}")
           break


model = torch.hub.load(r'C:\Users\rchitale\OneDrive\OneDrive - JLR\Desktop\yolov5', 'custom', path=r'C:\Users\rchitale\OneDrive\OneDrive - JLR\Desktop\yolov5\runs\train\run_8325\weights\last.pt', source='local') 
# Reference: https://medium.com/@aaparikh_/pothole-detection-using-yolov5-f605f6eb4d9c
# Training Command Used : python train.py --img 832 --cfg '.\models\yolov5m.yaml' --batch 16 --data '..\hackathon\data.yaml' --weights yolov5m.pt --name run_832 --epochs 10 --device 0

def display_frame(image, objects=None):
    if objects is not None and len(objects) > 0:
        for i in range(len(objects)):
            start_point = ( int(objects.at[i,'xmin']), int(objects.at[i,'ymin']))
            end_point = (int(objects.at[i,'xmax']), int(objects.at[i,'ymax']))
            cv2.rectangle(image, start_point, end_point, (250,250,250), 2) 

    cv2.imshow('display', image)
    cv2.waitKey(delay=1)
    # global frame_num
    # frame_num+=1
    # cv2.imwrite(f"pothole-frames\\pothole-frames-{frame_num}.jpg", image)   # Saves the frames with frame-count 

# frame_num = 0
def FrameCapture(): 
    path = r"C:\Users\rchitale\Downloads\video-potholes.mp4"
    vidObj = cv2.VideoCapture(path)    
    count = 0
    success = 1

    occurences = {"pothole":0}
    hazards = []
    start_time = time.time()

    plt.show()
    while success: 
        success, image = vidObj.read() 
        count += 1
        # if count % 4 != 0: continue          # do not need to check every frame
        results = model(image)
        res = results.pandas().xyxy[0]  
        occurences["pothole"] += len(res)      # currently trained for potholes, can be extended to other hazards
        display_frame(image,res)

        if time.time() - start_time > 5: break
    cv2.destroyAllWindows() 

    DANGER_THRESHOLD = 2
    if occurences["pothole"]/count > DANGER_THRESHOLD:
        hazards.append("pothole")
    return hazards

if __name__ == "__main__":
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
       s.connect(ADDR)
       # Start a thread to listen for server messages
       listener_thread = threading.Thread(target=listen_for_server_messages, args=(s,))
       listener_thread.daemon = True
       listener_thread.start()
       try:
           while True:
               SENSORS["latitude"] += 1
               SENSORS["longitude"] += 1
               hazards = FrameCapture()     
               vehicle_data = create_json_file(hazards)
               send_json_data(vehicle_data, s)
               # time.sleep(5)
       except KeyboardInterrupt:
           s.send(DISCONNECT_MESSAGE.encode(FORMAT))
           print("Disconnected from server.")



