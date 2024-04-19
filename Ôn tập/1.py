# Viết chương trình tự động bật tắt đèn LED theo chu kỳ 1s, hiển thị số lần đèn đã sáng lên terminal.
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
GPIO.setup(LED, GPIO.OUT)
try:
  while True:
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED, GPIO.LOW)
    time.sleep(1)
except KeyboardInterrupt:
  GPIO.cleanup()

