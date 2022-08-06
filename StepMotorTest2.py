import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM) #read the pin as board instead of BCM pin


LinearActuatorDir = 24
LinearActuatorStepPin = 23
LinearActuatorEnable = 18
#LinearActuatorDir = 25
#LinearActuatorStepPin = 22
#LinearActuatorEnable = 17

PowerToStep = 26



GPIO.setwarnings(False)
GPIO.setup(LinearActuatorDir, GPIO.OUT)
GPIO.setup(LinearActuatorStepPin, GPIO.OUT)
GPIO.setup(LinearActuatorEnable, GPIO.OUT)
GPIO.setup(PowerToStep, GPIO.OUT)



FastSpeed = 0.00045 #Change this depends on your stepper motor
LowSpeed = 0.00045
Speed = FastSpeed

GPIO.output(LinearActuatorEnable, GPIO.HIGH)
GPIO.output(PowerToStep, GPIO.HIGH)

while True:
	print ("Move Backward")
	for i in range (5*200):
		GPIO.output(LinearActuatorDir, 0)
		GPIO.output(LinearActuatorStepPin, 1)
		time.sleep(LowSpeed)
		GPIO.output(LinearActuatorStepPin, 0)
		time.sleep(LowSpeed)
		print ("Moving")
	time.sleep(1)
	print ("Move Forward")
	for i in range (5*200):
		GPIO.output(LinearActuatorDir, GPIO.HIGH)
		GPIO.output(LinearActuatorStepPin, GPIO.HIGH)
		time.sleep(FastSpeed)
		GPIO.output(LinearActuatorStepPin, GPIO.LOW)
		time.sleep(FastSpeed)
	time.sleep(1)