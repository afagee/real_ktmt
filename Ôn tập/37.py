# Phát triển một chương trình để hiển thị các ký tự nhận được từ một điều khiển từ xa hồng ngoại và điều khiển rơ le
# tương ứng với các phím nhất định. Cụ thể là khi nhấn button 1 lần 1, chương trình sẽ kích hoạt relay 1 và khi bấm
# button 1 lần 2 relay 1 sẽ được tắt. Khi nhấn button 2 lần 1, relay 2 được kích hoạt và khi nhấn button 2 lần 2, relay 2
# được tắt, cứ lặp đi lặp lại quá trình này.
# Phát triển một chương trình để hiển thị các ký tự nhận được từ một điều khiển từ xa hồng ngoại và điều khiển rơ le
# tương ứng với các phím nhất định. Cụ thể là khi nhấn phím 8, chương trình sẽ kích hoạt relay 1; nhấn phím 9,
# chương trình sẽ kích hoạt relay 2 và khi nhấn phím 0 sẽ tắt cả 2 relay này.
import RPi.GPIO as GPIO
import time

LCD_IR_SSS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
IR_SS = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IR_SS, GPIO.IN, GPIO.PUD_UP)


def lcd_init():
    for pin in LCD_IR_SSS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_IR_SSS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_IR_SSS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_IR_SSS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_IR_SSS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_IR_SSS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_IR_SSS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_IR_SSS['E'], False)
    time.sleep(E_DELAY)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def read_IR(IR_SS):
    while True:
        if GPIO.input(IR_SS) == 0:
            count = 0
            while GPIO.input(IR_SS) == 0 and count < 200:
                count += 1
                time.sleep(0.00006)
            count = 0
            while GPIO.input(IR_SS) == 1 and count < 80:
                count += 1
                time.sleep(0.00006)
            idx = 0
            cnt = 0
            data = [0, 0, 0, 0]
            for i in range(0, 32):
                count = 0
                while GPIO.input(IR_SS) == 0 and count < 15:
                    count += 1
                    time.sleep(0.00006)
                count = 0
                while GPIO.input(IR_SS) == 1 and count < 40:
                    count += 1
                    time.sleep(0.00006)
                if count > 8:
                    data[idx] |= 1 << cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1
            if data[0] + data[1] == 0xFF and data[2] + data[3] == 0xFF:
                #print("Get the key: 0x%02x" % data[2])
                #print(exec_cmd(data[2]))
                return data[2]


def exec_cmd(key_val):
    if key_val == 0x45:
        return "Button: CH- "
    elif key_val == 0x46:
        return "Button: CH  "
    elif key_val == 0x47:
        return "Button: CH+ "
    elif key_val == 0x44:
        return "Button: PREV"
    elif key_val == 0x40:
        return "Button: NEXT"
    elif key_val == 0x43:
        return "Button: P/PA"
    elif key_val == 0x07:
        return "Button: VOL- "
    elif key_val == 0x15:
        return "Button: VOL+ "
    elif key_val == 0x09:
        return "Button: EQ  "
    elif key_val == 0x16:
        return "Button: 0   "
    elif key_val == 0x19:
        return "Button: 100+"
    elif key_val == 0x0d:
        return "Button: 200+"
    elif key_val == 0x0c:
        return "Button: 1   "
    elif key_val == 0x18:
        return "Button: 2   "
    elif key_val == 0x5e:
        return "Button: 3   "
    elif key_val == 0x08:
        return "Button: 4   "
    elif key_val == 0x1c:
        return "Button: 5   "
    elif key_val == 0x5a:
        return "Button: 6   "
    elif key_val == 0x42:
        return "Button: 7   "
    elif key_val == 0x52:
        return "Button: 8   "
    elif key_val == 0x4a:
        return "Button: 9   "


RELAY1 = 16
GPIO.setup(RELAY1, GPIO.OUT)
RELAY2 = 12
GPIO.setup(RELAY2, GPIO.OUT)

def main():
    lcd_init()
    lcd_display_string("Ready for decode", 1)
    GPIO.output(LCD_IR_SSS["BL"], True)
    time.sleep(1)

    pressed_time_bt1 = 0
    pressed_time_bt2 = 0
    while True:
        reader = read_IR(IR_SS)
        if reader == 0x0c:
            pressed_time_bt1 += 1
            if pressed_time_bt1 % 2:
                GPIO.output(RELAY1, GPIO.HIGH)
            else:
                GPIO.output(RELAY1, GPIO.LOW)
        if reader == 0x18:
            pressed_time_bt2 += 1
            if pressed_time_bt2 % 2:
                GPIO.output(RELAY2, GPIO.HIGH)
            else:
                GPIO.output(RELAY2, GPIO.LOW)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
