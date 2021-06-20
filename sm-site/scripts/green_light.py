import RPi.GPIO as GPIO
import time
import sys

green_light = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(green_light, GPIO.OUT)
GPIO.setwarnings(False)

if __name__ == "__main__":
    print(str(sys.argv))
    # print(str(sys.argv[1]))
    if len(sys.argv) > 1:
        turn_type = sys.argv[1]
        if turn_type == "on":
            GPIO.output(green_light, 1)
            print("Turned on")
        if turn_type == "off":
            GPIO.output(green_light, 0)
            print("Turned off")
#GPIO.cleanup()

