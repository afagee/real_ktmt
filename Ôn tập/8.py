# Viết chương trình đóng ngắt relay 1 và relay 2 luân phiên với chu kỳ 1s.
import RPi.GPIO as GPIO
import time

RELAY_1 = 16
RELAY_2 = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)

try:
    while True:
        GPIO.output(RELAY_1, GPIO.HIGH)
        GPIO.output(RELAY_2, GPIO.LOW)
        time.sleep(1)
        GPIO.output(RELAY_1, GPIO.LOW)
        GPIO.output(RELAY_2, GPIO.HIGH)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()