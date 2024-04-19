# Viết chương trình thực hiện theo kịch bản sau: Ban đầu, đặt động cơ RC servo ở vị trí 90 độ.
# Mỗi khi bấm button 1 động cơ giảm dần góc quay 10 độ, khi quay đến góc 10 độ thì dừng lại.
# Mỗi khi bấm button 2, động cơ tăng dần góc quay 10 độ, khi quay đến góc 160 độ thì dừng lại.
# Khi bấm button 3 sẽ thiết lập góc quay đến 90 độ, hiển thị giá trị góc quay lên màn hình LCD.
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)
current_angle = 0

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}

BT_1 = 21
BT_2 = 26
BT_3 = 20
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm.ChangeDutyCycle(0)

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
    global current_angle
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    current_angle = 90
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            while GPIO.input(BT_1) == GPIO.LOW:
                current_angle -= 10
                if current_angle < 10:
                    current_angle = 10
                time.sleep(0.1)
        if GPIO.input(BT_2) == GPIO.LOW:
            while GPIO.input(BT_2) == GPIO.LOW:
                current_angle += 10
                if current_angle > 160:
                    current_angle = 160
                time.sleep(0.1)
        if GPIO.input(BT_3) == GPIO.LOW:
            current_angle = 90

        lcd_display_string(f"Goc quay:{current_angle} *", 1)
        set_servo_angle(current_angle)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
