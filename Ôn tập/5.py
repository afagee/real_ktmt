# Viết chương trình bấm button 1 lần 1 đèn LED sáng, bấm button 1 lần 2 thì đèn LED tắt, quá trình này lặp đi lặp lại.
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
buttonPin = 21
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
ledState = False


def updateLed():
    global ledState
    if GPIO.input(buttonPin) == GPIO.LOW:
        ledState = not ledState
        GPIO.output(ledPin, ledState)
        time.sleep(0.25)


try:
    while True:
        updateLed()
except KeyboardInterrupt:
    GPIO.cleanup()
