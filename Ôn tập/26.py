# Phát triển một chương trình để mô phỏng hệ thống điều khiển tự động công tắc đèn chiếu sáng,
# với cơ chế hoạt động như sau: khi môi trường xung quanh sáng, cả hai relay (relay 1 và relay 2)
# sẽ tự động ngắt, ngăn không cho đèn hoạt động; ngược lại, khi trời tối, relay 1 sẽ đóng ngay
# lập tức để kích hoạt đèn, tiếp theo, sau một khoảng thời gian chờ là 3 giây, relay 2 cũng đóng
# để hoàn thành cấu hình hệ thống chiếu sáng hoặc kích hoạt một bộ đèn khác, trong quá trình hoạt động,
# hiển thị trạng thái các relay lên màn hình LCD.
import RPi.GPIO as GPIO
import time

LIGHT_SS = 5
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

RELAY_1 = 16
RELAY_2 = 12
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)

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
    lcd_clear()
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def main():
    lcd_init()
    time.sleep(0.5)
    GPIO.setup(LIGHT_SS, GPIO.IN, GPIO.PUD_UP)
    GPIO.output(LCD_PINS['BL'], True)

    time_from = 0
    current_time = 0
    while True:
        if GPIO.input(LIGHT_SS) == GPIO.LOW:
            time_from = 0
            current_time = 0
            GPIO.output(RELAY_1, GPIO.LOW)
            GPIO.output(RELAY_2, GPIO.LOW)
        else:
            GPIO.output(RELAY_1, GPIO.HIGH)
            if time_from == 0:
                time_from = time.time()
            current_time = time.time()
            if current_time - time_from > 3:
                GPIO.output(RELAY_2, GPIO.HIGH)

        lcd_display_string("Relay 1 is " + ("ON" if GPIO.input(RELAY_1) else "OFF"), LCD_LINE1)
        lcd_display_string("Relay 2 is " + ("ON" if GPIO.input(RELAY_2) else "OFF"), LCD_LINE2)
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()
