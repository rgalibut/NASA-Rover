from flask import Flask, render_template, Response, request
from appCam import Camera
from gpiozero import Servo, Robot
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
import threading
import os

#Define Motor Driver GPIO pins
# Motor A, LEFT
PWML = 21     # PWMA - H-Bridge enable pin
FL = 16   # AI1 - Forward Drive
RL = 20   # AI2 - Reverse Drive
# Motor B, RIGHT
PWMR = 5     # PWMB - H-Bridge enable pin
FR = 19  # BI1 - Forward Drive
RR = 13  # BI2 - Reverse Drive
# PAN AND TILT PINS
PANPIN = 25
TILTPIN = 27

# SET PIN FACTORY FOR SERVOS
ping_fac = PiGPIOFactory()
pan = Servo(PANPIN, pin_factory = ping_fac)
tilt = Servo(TILTPIN, pin_factory = ping_fac)

# ROVER
rover = Robot((FL,RL,PWML), (FR,RR,PWMR))

# MOTOR SPEED
FSPD = 0.5
BSPD = 0.6
TSPD = 0.7
CSPD = 1.0

# App Globals (do not edit)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    if deviceName == "pan":
        actuator = pan
    if deviceName == "tilt":
        actuator = tilt
    if deviceName == "rover":
        actuator = rover
    if action == "max":
        if actuator.value < 1:
            actuator.value += 0.2
        sleep(0.005)
    if action == "min":
        if actuator.value > -1:
            actuator.value -= 0.2
        sleep(0.005)
    if action == "mid":
        pan.mid()
        tilt.mid()
        sleep(0.005)
    if action == "forward":
        actuator.forward(FSPD)
    if action == "backward":
        actuator.backward(BSPD)
    if action == "stop":
        actuator.stop()
    if action == "left":
        actuator.left(TSPD)
    if action == "right":
        actuator.right(TSPD)
    if action == "backLeft":
        actuator.left()
        actuator.reverse()
    if action == "backRight":
        actuator.right()
        actuator.reverse()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
