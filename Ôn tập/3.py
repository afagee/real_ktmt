# Viết chương trình thực hiện chức năng, khi đèn LED sáng thì đèn nền màn hình LCD tắt, ngược lại đèn LED tắt thì đèn nền màn hình LCD sáng. Quá trình này lặp đi lặp lại theo chu kỳ 1s
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
LCD_BL = 2
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LCD_BL, GPIO.OUT)


def toggleLED_LCD():
    GPIO.output(LED, not GPIO.input(LED))
    GPIO.output(LCD_BL, not GPIO.input(LCD_BL))


try:
    while True:
        toggleLED_LCD()
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
