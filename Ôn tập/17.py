# Viết chương trình mô phỏng bộ điều khiển độ ẩm trong phòng, khi độ ẩm cao hơn
# một ngưỡng cho trước thì nhấp nháy đèn LED cảnh báo, độ ẩm giảm dưới ngưỡng cho
# trước thì tắt đèn LED. Hiển thị giá trị độ ẩm lên màn hình LCDimport RPi.GPIO as GPIO
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
LED = 13
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)

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


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(1)

    warning_humidity = 60
    led_state = GPIO.LOW

    while True:
        temperature, humidity = read_dht11()
        print(temperature, humidity)
        if humidity is not None and temperature is not None:
            # lcd_display_string('temp: {:.1f}*C'.format(temperature), 1)
            lcd_display_string('humid: {:.1f}%'.format(humidity), 2)
            if humidity < warning_humidity:
                led_state = GPIO.LOW
            else:
                led_state = not led_state

            GPIO.output(LED, led_state)
            time.sleep(0.5)
        else:
            time.sleep(0.5)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()


