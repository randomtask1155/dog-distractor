#from keras.applications.resnet50 import ResNet50
#from keras.applications.imagenet_utils import decode_predictions
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing import image             
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tqdm import tqdm
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Lock
import numpy as np
import cv2
import time
import os

ResNet50_model_ = ResNet50(weights='imagenet')

def path_to_tensor(img_path):
    #img = image.load_img(img_path, target_size=(224, 224))
    #x = image.img_to_array(img)
    x = image.img_to_array(img_path)
    return np.expand_dims(x, axis=0)

def paths_to_tensor(img_paths):
    list_of_tensors = [path_to_tensor(img_path) for img_path in tqdm(img_paths)]
    return np.vstack(list_of_tensors)

def ResNet50_predict_labels(img_path):
    img = preprocess_input(path_to_tensor(img_path))
 
    predictions = ResNet50_model_.predict(img)
    #print(predictions, flush=True)
    labels = decode_predictions(predictions)
    #class_index = np.argmax(predictions)
    print(labels, flush=True)
    #print("prediction class: " + predictions[0][class_index], flush=True)
    return np.argmax(predictions)

    #return np.argmax(ResNet50_model_.predict(img))

def dog_detector(img_path):
    prediction = ResNet50_predict_labels(img_path)
    print(prediction, flush=True)
    return ((prediction <= 268) & (prediction >= 151))

#dog_detector("./test.jpg")
#print(dog_detector("./test.jpg"))

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#cv2.namedWindow("Input")
cap_mutex = Lock()

def scan_for_dog(duration=15):

    while duration > 0:
        ret, frame = cap.read() 
        ret, frame = cap.read() ## run twice to discard the old frame
        if ret != True:
            print("faled to get image", flush=True)
        success = dog_detector(cv2.resize(frame, (224, 224)))
        if success:
            print("detected dog", flush=True)
            os.system("play -q /home/pi/bin/noise.wav")
            print("audio file completed", flush=True)
            break
        else:
            print("not a dog", flush=True)
        duration -= 1
        time.sleep(1)

    cap_mutex.release()
    print("released lock", flush=True)

class motionHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        # try to grab lock without blocking and start processing
        if cap_mutex.acquire(blocking=False) and cap.isOpened():
            print("acquired lock", flush=True)
            t = Thread(target = scan_for_dog)
            t.start()
        else:
            if cap.isOpened():
                print("did not acquire lock", flush=True)
            else:
                print("video capture is closed", flush=True)
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

with HTTPServer(('', 8000), motionHandler) as server:
    server.serve_forever()

#cap.release()                           
#cv2.destroyAllWindows()
