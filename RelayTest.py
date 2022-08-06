#!/usr/bin/env python

import time

import RPi.GPIO as GPIO

PIN = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, GPIO.LOW)

for x in range (0,100):
    GPIO.output(PIN, GPIO.LOW)
    print ("Pin 6 Low")
    time.sleep(3.0)

    GPIO.output(PIN, GPIO.HIGH)
    print ("Pin 6 High")
    time.sleep(3.0)



GPIO.cleanup()