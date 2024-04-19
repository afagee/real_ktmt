# Viết chương trình bấm button 1 đóng relay 1 và ngắt relay 2, bấm button 2 thì đảo trạng thái các relay này, hiển thị trạng thái từng relay lên terminal.
import RPi.GPIO as GPIO
import time

RELAY_1 = 16
RELAY_2 = 12
BT_1 = 21
BT_2 = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def print_relay_status():
    print("Relay 1 is " + ("ON" if GPIO.input(RELAY_1) else "OFF"))
    print("Relay 2 is " + ("ON" if GPIO.input(RELAY_2) else "OFF"))


try:
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            GPIO.output(RELAY_1, GPIO.HIGH)
            GPIO.output(RELAY_2, GPIO.LOW)
            print("BUTTON 1 is pressed")
            print_relay_status()
            time.sleep(0.25)

        if GPIO.input(BT_2) == GPIO.LOW:
            GPIO.output(RELAY_1, GPIO.LOW)
            GPIO.output(RELAY_2, GPIO.HIGH)
            print("BUTTON 2 is pressed")
            print_relay_status()
            time.sleep(0.25)


except KeyboardInterrupt:
    GPIO.cleanup()