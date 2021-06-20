import time
from datetime import datetime
import RPi.GPIO as GPIO
import math
import threading

GPIO.setmode(GPIO.BOARD)

# Unstrasonic sensor
GPIO_TRIGGER = 7
GPIO_ECHO    = 11
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  
GPIO.setup(GPIO_ECHO,GPIO.IN)      
GPIO.output(GPIO_TRIGGER, False)

# Leds
red_led = 38
green_led = 40
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)

# Light duration
LIGHT_DURATION = 10
BETWEEN_DISTANCE_MEASURE = 0.5
BETWEEN_SPEED_MEASURES = 1

# No Warnings
GPIO.setwarnings(False)
RED_INTRERUPT = False

# 0 is green
# 1 is red
TRAFFIC_STATE = 0
# Settle the sensor

time.sleep(0.5)

def track_distance():
    
    # get the first distance (cm)
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start_1 = time.time()
    while GPIO.input(GPIO_ECHO)==0:
        start_1 = time.time()
    while GPIO.input(GPIO_ECHO)==1:
        stop_1 = time.time()
    elapsed_1 = stop_1-start_1
    distance_1 = elapsed_1 * 34300
    distance_1 = distance_1 / 2
    
    # wait between scans
    time.sleep(BETWEEN_DISTANCE_MEASURE)
    
    # get the second distance (cm)
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start_2 = time.time()
    while GPIO.input(GPIO_ECHO)==0:
        start_2 = time.time()
    while GPIO.input(GPIO_ECHO)==1:
        stop_2 = time.time()
    elapsed_2 = stop_2-start_2
    distance_2 = elapsed_2 * 34000
    distance_2 = distance_2 / 2
    
    # calculate the distance
    distance_changed = distance_1 - distance_2
    distance_changed = distance_changed / 5
    velocity_final = math.fabs(distance_changed)
    
    # if smaller than .4 is error
    if velocity_final < .4:
        velocity_final = 0
        
    return (distance_1, distance_2, velocity_final)
    

def flicker_traffic_light():
    global RED_INTRERUPT
    global TRAFFIC_STATE
    global green_led
    global red_led
    while True:
        if RED_INTRERUPT is True:
            print("Red interrupt is on")
            # Open red 
            GPIO.output(green_led, 0)
            GPIO.output(red_led, 1)
            TRAFFIC_STATE = 1
            
            # Wait red
            time.sleep(LIGHT_DURATION)
            
            # open green
            GPIO.output(green_led, 1)
            GPIO.output(red_led, 0)
            TRAFFIC_STATE = 0
            
            # Reset flag
            RED_INTRERUPT = False
            print("Red interrupt is off")
        else:
            # Wait duration
            for i in range(0, LIGHT_DURATION):
                time.sleep(1)
                if RED_INTRERUPT is True:
                    break
            
            if RED_INTRERUPT is True:
                continue
            
            if TRAFFIC_STATE == 0:
                TRAFFIC_STATE = 1
                
                # Open red
                GPIO.output(green_led, 0)
                GPIO.output(red_led, 1)
            else:
                # Open green
                GPIO.output(green_led, 1)
                GPIO.output(red_led, 0)



if __name__ == "__main__":
    # Light tick thread
    light_thread = threading.Thread(target = flicker_traffic_light)
    light_thread.start()
    
    try:
        while True:
            # sleep 1 seconds between mesures
            time.sleep(BETWEEN_SPEED_MEASURES)
            
            # if the interrupt is red, wait for it
            if RED_INTRERUPT is False:
                distance_1, distance_2, velocity = track_distance()
                # print ("Distance 1: ", distance_1)
                # print ("Distance 2: ", distance_2)
                # print ("Velocity : %.1f cm/s" % velocity)
                
                speed_limit_file = open("speed-limit.txt", "r")
                speed_limit = float(speed_limit_file.read())
                print(str(velocity))
                if velocity > speed_limit and velocity < 700:
                    # fac semafortul rosu
                    RED_INTRERUPT = True
                    
                    # inregistrez in fisier schimbarea
                    data_file = open("speed-data.txt", "a")
                    
                    # write the data to file
                    now = datetime.now()
                    date_time = now.strftime("%m/%d-%H:%M:%S")
                    
                    data_file.write(str(date_time) + " " + str(velocity) + "\n")
                    
                    # close the file
                    data_file.close();
                
            
        
    except KeyboardInterrupt:
        GPIO.cleanup()   
