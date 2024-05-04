# Phát triển một mô hình điều khiển tự động cho nhiệt độ và độ ẩm trong kho bảo quản đông lạnh, sử dụng cảm biến
# DHT11 để theo dõi môi trường, các button để cài đặt thông số mong muốn, và các relay để điều khiển thiết bị
# công suất giúp giữ môi trường ổn định. Mô tả chi tiết: Sử dụng cảm biến DHT11 để đo nhiệt độ và độ ẩm trong kho.
# Dữ liệu thu thập sẽ được dùng để điều chỉnh môi trường bảo quản. Button được sử dụng để cài đặt các giới hạn nhiệt độ
# và độ ẩm mong muốn. Các thông số nhiệt độ, độ ẩm được hiển thị trên màn hình LCD. Để ổn định nhiệt độ, độ ẩm,
# chúng ta sử dụng các thiết bị công suất thông qua các relay

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
DHT11 = 7
BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19
RELAY1 = 16
RELAY2 = 12
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_dht11():
    GPIO.setup(DHT11, GPIO.OUT)
    GPIO.output(DHT11, GPIO.LOW)
    time.sleep(0.05)
    GPIO.output(DHT11, GPIO.HIGH)
    GPIO.setup(DHT11, GPIO.IN)

    while GPIO.input(DHT11) == GPIO.LOW:
        pass
    while GPIO.input(DHT11) == GPIO.HIGH:
        pass

    data = []
    for i in range(40):
        while GPIO.input(DHT11) == GPIO.LOW:
            pass
        count = 0
        while GPIO.input(DHT11) == GPIO.HIGH:
            count += 1
            if count > 100:
                break
        if count > 8:
            data.append(1)
        else:
            data.append(0)
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check_sum = 0

    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        check_sum += check_bit[i] * 2 ** (7 - i)

    check = humidity + humidity_point + temperature + temperature_point
    if check_sum == check:
        return temperature + temperature_point, humidity + humidity_point
    else:
        return None, None


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


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
    lcd_byte(LCD_LINE1 if line == 1 else LCD_LINE2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


temperature_wanted = [26, 27, 28, 29]
humidity_wanted = [75, 70, 65, 60]


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(1)

    global temperature_wanted, humidity_wanted
    while True:
        bt_pressed = -1

        if GPIO.input(BT1) == GPIO.LOW:
            bt_pressed = 0
        if GPIO.input(BT2) == GPIO.LOW:
            bt_pressed = 1
        if GPIO.input(BT3) == GPIO.LOW:
            bt_pressed = 2
        if GPIO.input(BT4) == GPIO.LOW:
            bt_pressed = 3

        if bt_pressed != -1:
            current_temp, current_humidity = read_dht11()

            if int(current_temp) != temperature_wanted[bt_pressed]:
                GPIO.output(RELAY1, GPIO.HIGH)
            else:
                GPIO.output(RELAY1, GPIO.LOW)

            if int(current_humidity) != humidity_wanted[bt_pressed]:
                GPIO.output(RELAY2, GPIO.HIGH)
            else:
                GPIO.output(RELAY2, GPIO.LOW)



try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()
