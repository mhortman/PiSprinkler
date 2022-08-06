#!/usr/bin/env python
#!/usr/bin/python
import time, threading
import RPi.GPIO as GPIO
import json
from numpy import loadtxt

from flask import request
from flask_api import FlaskAPI

VALVE_PIN = 21

#LinearActuatorDir = 24
#LinearActuatorStepPin = 23
#LinearActuatorEnable = 18
LinearActuatorDir = 25
LinearActuatorStepPin = 22
LinearActuatorEnable = 17


BASE_DIR = 25
BASE_STEP_PIN = 22
BASE_ENABLE_PIN = 17
VERT_DIR = 24
VERT_STEP_PIN = 23
VERT_ENABLE_PIN = 18
POWER_TO_STEPPER = 26
PLAYBACK_FILE = 'playback.txt'


valve_state = 0
VALVE = {"on": 1, "off":0}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(VALVE_PIN, GPIO.OUT)
GPIO.output(VALVE_PIN, GPIO.LOW)

GPIO.setup(BASE_DIR, GPIO.OUT)
GPIO.setup(BASE_STEP_PIN, GPIO.OUT)
GPIO.setup(BASE_ENABLE_PIN, GPIO.OUT)

GPIO.setup(VERT_DIR, GPIO.OUT)
GPIO.setup(VERT_STEP_PIN, GPIO.OUT)
GPIO.setup(VERT_ENABLE_PIN, GPIO.OUT)
GPIO.setup(POWER_TO_STEPPER, GPIO.OUT)

STEP_MULTIPLIER = 20
FastSpeed = 0.00045 #Change this depends on your stepper motor
LowSpeed = 0.00045
Speed = FastSpeed
stepPower = 0

GPIO.output(VERT_DIR, GPIO.LOW)
GPIO.output(VERT_ENABLE_PIN, GPIO.LOW)
GPIO.output(BASE_DIR, GPIO.LOW)
GPIO.output(BASE_ENABLE_PIN, GPIO.LOW)
GPIO.output(POWER_TO_STEPPER, GPIO.LOW)

powerTimer = time.time() #start time

def powerDownSteppers():
    global stepPower
    print ("Power Step Off")
    stepPower= 0
    GPIO.output(POWER_TO_STEPPER, GPIO.LOW)


def checkIfTurnPowerOff():
    timeSincePC = time.time()-powerTimer
    if (timeSincePC > 10.0 and stepPower):
        powerDownSteppers()
    #print(f"Timer {powerTimer:0.4f}")
    #print(f"Time {time.time():0.4f}")
    print(f"Last Power Check {timeSincePC:0.4f}")
    threading.Timer(10, checkIfTurnPowerOff).start()
    
def resetPowerTimer():
    global powerTimer
    powerTimer = time.time() #start time

def powerSteppers():
    global stepPower
    resetPowerTimer()
    if not stepPower:
        time.sleep(0.2)
        print ("Power Step On")
        GPIO.output(POWER_TO_STEPPER, GPIO.HIGH)
        stepPower = 1

checkIfTurnPowerOff()


app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
    return {
           "valve_url": request.url + "valve/(on | off)/", "valve_url_POST": {"state": "(0 | 1)"},
           "vert_url": request.url + "vert/(degrees)/", "valve_url_POST": "(degrees)",
           "base_url": request.url + "base/(degrees)/", "base_url_POST": "(degrees)"
        }
  
@app.route('/valve/<state>/', methods=["GET", "POST"])
def api_valve_control(state):
    print('Valve control')
    if request.method == "POST":
        if state in VALVE:
            #GPIO.output(VALVE_PIN, int(request.data.get("state")))
            GPIO.output(VALVE_PIN, VALVE[state])
    return {state: GPIO.input(VALVE_PIN)}

@app.route('/base/<degrees>/', methods=["GET", "POST"])
def base_turn(degrees):
    powerSteppers()
    fdegrees = float(degrees)
    if request.method == "POST":
        print ('Base Turn '+degrees)
        GPIO.output(BASE_ENABLE_PIN, GPIO.HIGH)
    
        if fdegrees> 0.0:
            print ("Move Forward")
            for i in range (int(fdegrees*STEP_MULTIPLIER)):
                GPIO.output(BASE_DIR, GPIO.HIGH)
                GPIO.output(BASE_STEP_PIN, GPIO.HIGH)
                time.sleep(FastSpeed)
                GPIO.output(BASE_STEP_PIN, GPIO.LOW)
                time.sleep(FastSpeed)
           # time.sleep(1)
        if fdegrees < 0.0:
            print ("Move Backward")
            for i in range (int(-1*fdegrees*STEP_MULTIPLIER)):
                GPIO.output(BASE_DIR, 0)
                GPIO.output(BASE_STEP_PIN, 1)
                time.sleep(LowSpeed)
                GPIO.output(BASE_STEP_PIN, 0)
                time.sleep(LowSpeed)
        GPIO.output(BASE_DIR, GPIO.LOW)
        GPIO.output(BASE_ENABLE_PIN, GPIO.LOW)
        time.sleep(100/1000)
            
    return {}

@app.route('/vert/<degrees>/', methods=["GET", "POST"])
def vert_turn(degrees):
    powerSteppers()
    fdegrees = float(degrees)
    if request.method == "POST":
        print ('Vert Turn '+degrees)
        GPIO.output(VERT_ENABLE_PIN, GPIO.HIGH)
    
        if fdegrees> 0.0:
            print ("Move Forward")
            for i in range (int(fdegrees*STEP_MULTIPLIER)):
                GPIO.output(VERT_DIR, GPIO.HIGH)
                GPIO.output(VERT_STEP_PIN, GPIO.HIGH)
                time.sleep(FastSpeed)
                GPIO.output(VERT_STEP_PIN, GPIO.LOW)
                time.sleep(FastSpeed)
           # time.sleep(1)
        if fdegrees < 0.0:
            print ("Move Backward")
            for i in range (int(-1*fdegrees*STEP_MULTIPLIER)):
                GPIO.output(VERT_DIR, 0)
                GPIO.output(VERT_STEP_PIN, 1)
                time.sleep(LowSpeed)
                GPIO.output(VERT_STEP_PIN, 0)
                time.sleep(LowSpeed)

        GPIO.output(VERT_DIR, GPIO.LOW)
        GPIO.output(VERT_ENABLE_PIN, GPIO.LOW)
        time.sleep(100/1000)
            
    return {}

@app.route('/store/', methods=["POST"])
def store_playback():
    print ("In Store")
    content = request.json
    print (content)
    if request.method == "POST":
        print ("In Store")
        with open(PLAYBACK_FILE, "w") as fp:
            json.dump(content, fp) 
        
    return 'valid_store'

@app.route('/PowerOff/', methods=["GET", "POST"])
def power_down(degrees):
    powerDownSteppers()
    return 'Off'

@app.route('/listAll/', methods=["GET"])
def load_playback():
    b = []
    if request.method == "GET":
        with open(PLAYBACK_FILE, "r") as fp:
            b = json.load(fp)
    print(" List All ",b)
    
    return {'playlist':b}


if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=8080)


