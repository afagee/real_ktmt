# Viết chương trình bấm button 1 đèn LED sáng, bấm button 2 đèn LED tắt, bấm button 3 đèn LED nhấp nháy theo chu kỳ 1s, bấm button 4 lần 1 đèn LED sáng, lần 2 đèn LED tắt. Hiển thị trạng thái các phím đã bấm lên terminal.
from multiprocessing import Value, Process
import RPi.GPIO as GPIO
import time

BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19
LED = 13


def handle_BT1(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT1) == GPIO.LOW:
            print("Button 1 pressed")
            is_pressed_BT3.value = False
            pressed_time_BT4.value = 0
            GPIO.output(LED, GPIO.HIGH)
        time.sleep(0.15)


def handle_BT2(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT2) == GPIO.LOW:
            print("Button 2 pressed")
            is_pressed_BT3.value = False
            pressed_time_BT4.value = 0
            GPIO.output(LED, GPIO.LOW)
        time.sleep(0.15)


def handle_BT3(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT3) == GPIO.LOW:
            print("Button 3 pressed")
            is_pressed_BT3.value = True
            pressed_time_BT4.value = 0

        if is_pressed_BT3.value:
            GPIO.output(LED, not GPIO.input(LED))
            time.sleep(1)
        time.sleep(0.15)


def handle_BT4(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT4) == GPIO.LOW:
            print("Button 4 pressed")
            is_pressed_BT3.value = False
            pressed_time_BT4.value = (pressed_time_BT4.value % 2) + 1
            GPIO.output(LED, GPIO.HIGH if pressed_time_BT4.value == 1 else GPIO.LOW)
        time.sleep(0.15)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED, GPIO.OUT)
    pressed_time_BT4 = Value('d', 0)
    is_pressed_BT3 = Value('i', False)
    Process(target=handle_BT1, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT2, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT3, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT4, args=(is_pressed_BT3, pressed_time_BT4)).start()


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
