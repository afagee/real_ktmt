# Phát triển một chương trình để mô phỏng hệ thống chống xâm nhập sử dụng cảm biến siêu âm.
# Hệ thống sẽ theo dõi và phát hiện sự hiện diện của vật cản phía trước.
# Khi phát hiện vật cản, hệ thống bật đèn LED như một cảnh báo ban đầu.
# Khi khoảng cách giữa cảm biến và vật cản nhỏ hơn một ngưỡng xác định, hệ thống sẽ kích hoạt relay 1.
# Nếu tiếp tục sẽ làm quay động cơ DC để tăng cấp độ cảnh báo.
# Hiển thị các mức độ cảnh báo và thông tin về khoảng cách đến vật cản trên màn hình LCD.
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
LED = 13
RELAY1 = 16
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm_DIR = GPIO.PWM(PWM, 1000)
pwm_DIR.start(0)


def motor_control(speed, direction):
    GPIO.output(DIR, direction)
    pwm_DIR.ChangeDutyCycle(speed)


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    global pulse_end, pulse_start
    while True:
        if GPIO.input(BT_1) == 0:
            lcd_display_string("Dang thuc hien do", 1)
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
                lcd_display_string("Không có vật cản", 1)
                GPIO.output(LED, GPIO.HIGH)
                GPIO.output(RELAY1, GPIO.HIGH)
            else:
                if 50 < distance < 100:
                    GPIO.output(LED, GPIO.LOW)
                    GPIO.output(RELAY1, GPIO.HIGH)
                    motor_control(0, 0)
                    lcd_display_string("Canh bao 1", 1)
                    lcd_display_string("Distance: %scm" % distance, 2)
                elif 25 < distance <= 50:
                    GPIO.output(LED, GPIO.LOW)
                    GPIO.output(RELAY1, GPIO.LOW)
                    motor_control(0, 0)
                    lcd_display_string("Canh bao 2", 1)
                    lcd_display_string("Distance: %scm" % distance, 2)
                else:
                    GPIO.output(LED, GPIO.LOW)
                    GPIO.output(RELAY1, GPIO.LOW)
                    motor_control(50, 0)
                    lcd_display_string("Canh bao 3", 1)
                    lcd_display_string("Distance: %scm" % distance, 2)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()