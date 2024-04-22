# Viết chương trình mô phỏng hệ thống bơm nước tự động. Hệ thống sẽ sử dụng cảm biến siêu âm để đo khoảng cách từ mặt
# thoáng đến mức nước trong bể. Dựa vào kết quả đo được, hệ thống sẽ tự động kích hoạt hoặc ngừng hoạt động của một động
# cơ DC để bơm nước vào hoặc ngừng bơm nước khỏi bể, nhằm duy trì mức nước trong một khoảng ngưỡng nhất định. Khoảng cách
# được đo cũng sẽ được hiển thị lên một màn hình LCD.
import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
BT_1 = 21
TRIG = 15
ECHO = 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)

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


pulse_end = 0
pulse_start = 0

PWM = 24
DIR = 25
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm = GPIO.PWM(PWM, 1000)
pwm.start(0)

def motor_control(speed, direction):
    GPIO.output(DIR, direction)
    pwm.ChangeDutyCycle(speed)

def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    global pulse_end, pulse_start
    while True:
        time.sleep(2)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        if distance > 100:
            lcd_display_string("ERROR", 1)
        else:
            lcd_display_string("Distance: %scm" % distance, 1)
            if distance > 10:
                motor_control(50, 0)
            else:
                motor_control(0, 0)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()