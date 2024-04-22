# Phát triển chương trình mô phỏng một hệ thống điều khiển tự động ánh sáng cho nhà kính,
# sử dụng cảm biến ánh sáng để tự động điều chỉnh mức độ mở của rèm che tùy thuộc vào cường độ ánh sáng
# môi trường. Khi ánh sáng mạnh và vượt quá ngưỡng đã cài đặt, động cơ RC servo sẽ được kích hoạt để
# quay 120 độ, trong khi DC motor sẽ hoạt động cùng lúc để cuốn rèm, tối ưu hóa việc tiếp nhận ánh sáng.
# Ngược lại, khi cường độ ánh sáng giảm xuống dưới ngưỡng, DC motor sẽ quay ngược lại để đóng rèm.
# Sau đó, khoảng 3 giây, động cơ RC servo sẽ quay về góc 30 độ để khóa rèm,
# hiện các trạng thái lên màn hình LCD.
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
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


PWM = 24
DIR = 25
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm_DIR = GPIO.PWM(PWM, 1000)
pwm_DIR.start(0)


def motor_control(speed, direction):
    GPIO.output(DIR, direction)
    pwm_DIR.ChangeDutyCycle(speed)


SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm_SERVO = GPIO.PWM(SERVO, 50)
pwm_SERVO.start(0)


def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO, True)
    pwm_SERVO.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm_SERVO.ChangeDutyCycle(0)


def main():
    lcd_init()
    time.sleep(0.5)
    GPIO.setup(LIGHT_SS, GPIO.IN, GPIO.PUD_UP)
    GPIO.output(LCD_PINS['BL'], True)

    motor_control(0, 0)
    set_servo_angle(30)

    time_from = 0
    current_time = 0
    rem_state = 0

    while True:
        if GPIO.input(LIGHT_SS) == GPIO.LOW:
            time_from = 0
            current_time = 0
            set_servo_angle(120)
            motor_control(30, 0)
            rem_state = 1
        else:
            motor_control(30, 1)

            if time_from == 0:
                time_from = time.time()
            current_time = time.time()
            if rem_state == 1 and current_time - time_from > 3:
                set_servo_angle(30)
                rem_state = 0

        lcd_display_string("Rem mo" if rem_state else "Rem dong", LCD_LINE1)
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()
