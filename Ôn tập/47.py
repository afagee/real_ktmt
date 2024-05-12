# Phát triển hệ thống giám sát an ninh với chức năng lưu trữ bằng chứng khi có xâm phạm trái phép.
# Mô tả chi tiết: Sử dụng cảm biến khoảng cách để phát hiện sự đột nhập trong khu vực được giám sát.
# Tùy thuộc vào khoảng cách giữa đối tượng đột nhập và cảm biến, hệ thống sẽ phân loại và phản ứng bằng các
# mức độ cảnh báo khác nhau. Ở mức cảnh báo đầu tiên, đèn LED sẽ nhấp nháy theo chu kỳ mỗi 1 giây.
# Khi chuyển sang mức cảnh báo thứ hai, relay sẽ được kích hoạt và camera sẽ bắt đầu phát trực tiếp hình ảnh.
# Trong trường hợp cảnh báo mức cao nhất, hệ thống không chỉ kích hoạt động cơ DC mà còn cho phép camera ghi
# lại các đoạn video có thời lượng 30 giây, được lưu trữ tự động vào thư mục video dành cho việc lưu trữ và
# phân tích sau này. Các mức độ cảnh báo được hiển thị trên màn hình LCD.

import RPi.GPIO as GPIO
from multiprocessing import Value, Process
import time
import cv2

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
LED = 13
TRIG = 15
ECHO = 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
RELAY1 = 16
RELAY2 = 12
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)
PWM = 24
DIR = 25
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm = GPIO.PWM(PWM, 1000)
pwm.start(0)

def motor_control(speed, direction):
    GPIO.output(DIR, direction)
    pwm.ChangeDutyCycle(speed)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def handle_distance(distance):
    pulse_end = 0
    pulse_start = 0

    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance.value = pulse_duration * 17150
        distance.value = round(distance, 2)


def handle_LED(distance):
    while True:
        if 30 > distance.value >= 20:
            lcd_display_string("Muc 1", 1)
            GPIO.output(LED, not GPIO.input(LED))
            time.sleep(1)
        else:
            GPIO.output(LED, GPIO.LOW)

def handle_mode(distance):
    cap = cv2.VideoCapture(0)
    out = cv2.VideoWriter('output.avi', fourcc=cv2.VideoWriter_fourcc(*'MJPG'), fps=20.0, frameSize=(640, 490))
    cv2.namedWindow('Camera')

    while True:
        if 20 > distance.value >= 10:
            lcd_display_string("Muc 2", 1)
            GPIO.output(RELAY1, GPIO.HIGH)
            GPIO.output(RELAY2, GPIO.HIGH)
        else:
            GPIO.output(RELAY1, GPIO.LOW)
            GPIO.output(RELAY2, GPIO.LOW)

        if distance.value < 10:
            lcd_display_string("Muc 3", 1)
            motor_control(50, 0)

        _, scr = cap.read()
        if distance < 20:
            cv2.imshow('Camera', scr)
        if distance < 10:
            out.write(scr)


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    distance = Value('d', 0)
    Process(target=handle_distance, args=distance).start()
    Process(target=handle_LED, args=distance).start()
    Process(target=handle_mode, args=distance).start()


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()