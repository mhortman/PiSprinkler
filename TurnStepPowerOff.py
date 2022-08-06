import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM) #read the pin as board instead of BCM pin


PowerToStep = 26

GPIO.setup(PowerToStep, GPIO.OUT)

GPIO.output(PowerToStep, GPIO.LOW)