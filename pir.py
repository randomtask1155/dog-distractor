import RPi.GPIO as GPIO
import time
import requests

PIN=8
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN,GPIO.IN)

def send_post():
    requests.post("http://192.168.86.127:8000")

while True:
    i=GPIO.input(PIN)
    if i == 1:
        print ("motion detected")
        send_post()
        time.sleep(1)
    time.sleep(0.3)

