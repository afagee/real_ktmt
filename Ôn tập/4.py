# Viết chương trình bấm button 1 thì đèn LED sáng, thả button 1 thì đèn LED tắt.
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
BT_1 = 21
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def updateLED():
    if GPIO.input(BT_1) == GPIO.LOW:
        GPIO.output(LED, GPIO.HIGH)
    else:
        GPIO.output(LED, GPIO.LOW)


try:
    while True:
        updateLED()
except KeyBoInterrupt:
    GPIO.cleanup()
