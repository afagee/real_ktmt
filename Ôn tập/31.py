# Viết chương trình hiển thị các ký tự lên LED matrix qua giao tiếp SPI
# sử dụng các câu lệnh thông thường
import RPi.GPIO as GPIO
import time
CLK = 11
DIN = 10
CS = 8

character = {
    'A': [0x3C, 0x66, 0xC3, 0xC3, 0xFF, 0xC3, 0xC3, 0xC3],
    'B': [0xFC, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x66, 0xFC],
    '0': [0x3C, 0x66, 0xC3, 0xC3, 0xC3, 0xC3, 0x66, 0x3C],
    '1': [0x10, 0x30, 0x10, 0x10, 0x10, 0x10, 0x10, 0x7C],
    '2': [0x3E, 0x63, 0x03, 0x0E, 0x1C, 0x30, 0x63, 0x7F],
    '+': [0x00, 0x18, 0x18, 0x7E, 0x7E, 0x18, 0x18, 0x00],
    '-': [0x00, 0x00, 0x00, 0x7E, 0x7E, 0x00, 0x00, 0x00],
    'x': [0x00, 0xC3, 0x66, 0x3C, 0x3C, 0x66, 0xC3, 0x00],
    '/': [0x03, 0x06, 0x0C, 0x18, 0x30, 0x60, 0xC0, 0x00],
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

def spi_send_byte(register, data):
    GPIO.output(CS, GPIO.LOW)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (register >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (data >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)

    GPIO.output(CS, GPIO.HIGH)

def max7219_init():
    spi_send_byte(0x0F, 0x00)
    spi_send_byte(0x09, 0x00)
    spi_send_byte(0x0B, 0x07)
    spi_send_byte(0x0A, 0x00)
    spi_send_byte(0x0C, 0x01)

def clear_display():
    for row in range(1, 9):
        spi_send_byte(row, 0x00)

def display_pattern(Character):
    for row in range(8):
        spi_send_byte(row + 1, Character[row])

def display_pattern_180(pattern):
    pattern_180 = [int('{:08b}'.format(row)[::-1], 2) for row in pattern[::-1]]
    for row in range(8):
        spi_send_byte(row + 1, pattern_180[row])

def main():
    max7219_init()
    clear_display()
    while True:
        time.sleep(1)
        display_pattern_180(character['A'])
        time.sleep(1)
        display_pattern(character['A'])
        time.sleep(1)
        clear_display()


try:
    main()
except KeyboardInterrupt:
    clear_display()
    GPIO.cleanup()