# Viết chương trình thực hiện chức năng như mô tả sau: sử dụng button 1
# và button 2 như các cảm biến tiệm cận, mô phỏng việc đếm số người vào
# trong phòng. Nếu button 1 bấm trước, button 2 bấm sau sẽ quy ước số người
# đi vào phòng, ngược lại nếu button 2 bấm trước, button 1 bấm sau sẽ quy ước
# số người đi ra khỏi phòng. Nếu có người trong phòng sẽ đóng relay để bật điện,
# nếu không có người trong phòng sẽ mở relay để tắt điện. Trong quá trình hoạt động
# sẽ hiển thị số người đi ra hoặc đi vào trong phòng và tổng số người còn lại trong
# phòng lên màn hình LCD.

import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
BT_2 = 26
RELAY_1 = 16
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1, GPIO.OUT)

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


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    dem = 0
    people_inside = 0

    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            time.sleep(0.25)
            while True:
                if GPIO.input(BT_2) == GPIO.LOW:
                    people_inside += 1
                    time.sleep(0.25)
                    lcd_display_string(f" So nguoi: {people_inside}", 1)
                    break
        if GPIO.input(BT_2) == GPIO.LOW:
            time.sleep(0.25)
            while True:
                if GPIO.input(BT_1) == GPIO.LOW:
                    people_inside -= 1
                    people_inside = max(0, people_inside)
                    time.sleep(0.25)
                    lcd_display_string(f" So nguoi: {people_inside}", 1)
                    break
        if people_inside > 0:
            GPIO.output(RELAY_1, GPIO.HIGH)
        else:
            GPIO.output(RELAY_1, GPIO.LOW)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()
