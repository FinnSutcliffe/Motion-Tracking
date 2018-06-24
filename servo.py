import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

px = GPIO.PWM(16, 50)
py = GPIO.PWM(12, 50)

px.start(7.5)
py.start(7.5)

try:
    while True:
        print "Restart"
        inp = raw_input()
        pos = ["", ""]
        space = False
        for x in inp:
            if x == " ":
                space = True
            if not space:
                pos[0] += x
            else:
                pos[1] += x
        print pos
        pos[0] = int(pos[0])/18.0 + 2.5
        pos[1] = int(pos[1])/18.0 + 2.5
        print pos
        px.ChangeDutyCycle(pos[0])
        py.ChangeDutyCycle(pos[1])
        #p.ChangeDutyCycle(7.5)  # turn towards 90 degree
        #time.sleep(1) # sleep 1 second
        #p.ChangeDutyCycle(2.5)  # turn towards 0 degree
        #time.sleep(1) # sleep 1 second
        #p.ChangeDutyCycle(12.5) # turn towards 180 degree
        #time.sleep(1) # sleep 1 second 
except KeyboardInterrupt:
    px.stop()
    py.stop()
    GPIO.cleanup()