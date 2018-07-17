import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setwarnings(False)
try:
    while True:
        if GPIO.input(15):
            print "1"
        if GPIO.input(22):
            print "2"
        sleep(0.2)
except:
    GPIO.cleanup()
        
    
    